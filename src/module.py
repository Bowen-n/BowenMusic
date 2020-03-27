import json
import math
import os
import random
import sys
import time
import urllib
from threading import Thread

from pymediainfo import MediaInfo
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *

from api import QQMusicApi, NeteaseCloudMusicAPI, MiguMusicAPI, convert_interval
from component import ImgLabel, SearchLineEdit


class Header(QFrame):
    ''' Containing Logo, SearchLine, Minimize and Close '''

    def __init__(self, parent=None):
        super(Header, self).__init__()
        self.setObjectName('Header')
        self.music_source = 'qq' # 'netease' or 'qq' or 'migu'
        # self.setWindowFlags(Qt.FramelessWindowHint)

        with open('qss/header.qss', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

        self.parent = parent
        
        self._set_buttons()
        self._set_labels()
        self._set_line_edits()
        self._set_lines()
        self._set_layouts()


    def _set_buttons(self):
        self.close_button = QPushButton('×', self)
        self.close_button.setObjectName('close_button')
        self.close_button.setMinimumSize(60, 35)
        self.close_button.setMaximumSize(60, 35)
        self.close_button.setStyle(QStyleFactory.create('Fusion'))
        self.close_button.setCursor(Qt.PointingHandCursor)

        self.min_button = QPushButton('—', self)
        self.min_button.setObjectName('min_button')
        self.min_button.setMinimumSize(60, 35)
        self.min_button.setMaximumSize(60, 35)
        self.min_button.setStyle(QStyleFactory.create('Fusion'))
        self.min_button.setCursor(Qt.PointingHandCursor)

        # self.max_button = QPushButton('口')
        # self.max_button.setObjectName('max_button')
        # self.max_button.setMaximumSize(16, 16)
        

    def _set_labels(self):
        self.logo_label = ImgLabel('resource/logo2.png', 55, 55)

        self.text_label = QLabel(self)
        self.text_label.setText("<b>BowenMusic<b>")


    def _set_line_edits(self):
        self.search_line = SearchLineEdit(self)
        self.search_line.setPlaceholderText("〇 搜索音乐, 歌手")
        self.search_line.returnPressed.connect(lambda: Thread(target=self.search).start())
        self.search_line.set_button_slot(lambda: Thread(target=self.search).start())


    def search(self):
        self.parent.main_list.music_list.clear()
        self.parent.navigation.local_list.setCurrentItem(None)
        self.parent.navigation.play_list.setCurrentItem(None)

        self.parent.main_list.display_mode = 'global'

        keywords = self.search_line.text()
        if keywords == '':
            return

        if self.music_source == 'qq':
            self.parent.navigation.navigation_list.setCurrentRow(0)
            api = QQMusicApi()
        elif self.music_source == 'netease':
            self.parent.navigation.navigation_list.setCurrentRow(1)
            api = NeteaseCloudMusicAPI()
        elif self.music_source == 'migu':
            self.parent.navigation.navigation_list.setCurrentRow(2)
            api = MiguMusicAPI()
        else:
            raise ValueError('music sources only contain qq, netease and migu.')

        search_result = []
        if api.name == 'qq':
            for page in [1, 2]:
                search_result += api.search(page, keywords)
        elif api.name == 'netease':
            search_result += api.search(keywords, 1)
        elif api.name == 'migu':
            search_result += api.search(keywords)
        else:
            raise ValueError('api.name not in qq, netease and migu')


        for item in search_result:
            qt_item = QTreeWidgetItem()
            qt_item.setText(0, item['song_name'])

            if api.name == 'migu':
                singers = item['singer_list']
            else:
                singers = ''
                for singer in item['singer_list']:
                    singers += singer
                    singers += '/'
                singers = singers.strip('/')

            qt_item.setText(1, singers)
            qt_item.setText(2, item['album_name'])

            if api.name == 'migu':
                qt_item.setText(3, '')
            else:
                qt_item.setText(3, convert_interval(item['interval']))

            qt_item.setText(4, str(item['song_mid']))
            
            if api.name == 'migu':
                qt_item.setText(5, item['url'])
            else:
                qt_item.setText(5, '')
            qt_item.setText(6, api.name)

            self.parent.main_list.music_list.addTopLevelItem(qt_item)


    def _set_lines(self):
        self.line1 = QFrame(self)
        self.line1.setObjectName('line1')
        self.line1.setFrameShape(QFrame.VLine)
        self.line1.setFrameShadow(QFrame.Plain)
        self.line1.setMaximumSize(1, 25)


    def _set_layouts(self):
        self.main_layout = QHBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.addSpacing(15)
        self.main_layout.addWidget(self.logo_label)
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(self.text_label)

        self.main_layout.addSpacing(200)

        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(self.search_line)

        self.main_layout.addStretch(1)
        self.main_layout.addSpacing(600)

        self.main_layout.addWidget(self.line1)
        self.main_layout.addSpacing(50)
        self.main_layout.addWidget(self.min_button)
        # self.main_layout.addWidget(self.max_button)
        self.main_layout.addWidget(self.close_button)

        self.setLayout(self.main_layout)


    ''' Reload the mouse event to drag the window 
    Ref: https://www.cnblogs.com/codeAB/p/5019439.html
    '''
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # self.setCursor(Qt.OpenHandCursor)
            self.parent.m_drag = True
            self.parent.m_DragPosition = event.globalPos() - self.parent.pos()
            event.accept()
    
    def mouseMoveEvent(self, event):
        try:
            if self.parent.m_drag and Qt.LeftButton:
                self.parent.move(event.globalPos() - self.parent.m_DragPosition)
                event.accept()
        except AttributeError:
            pass

    def mouseReleaseEvent(self, event):
        self.parent.m_drag = False

class Navigation(QScrollArea):
    search_music_signal = pyqtSignal()
    ''' On the left of the whole window
    Containing online music, local music and song list
    '''

    def __init__(self, parent=None):
        super(Navigation, self).__init__(parent)
        self.parent = parent
        self.frame = QFrame()
        self.setMaximumWidth(300)
        self.setMinimumWidth(300)

        self.setMinimumHeight(850)

        self.setWidget(self.frame)
        self.setWidgetResizable(True)
        self.frame.setMinimumWidth(300)

        self.playlist_count = 0

        with open('qss/navigation.qss', 'r') as f:
            style = f.read()
            self.setStyleSheet(style)
            self.frame.setStyleSheet(style)

        self._set_labels()
        self._set_list_views()
        self._set_buttons()
        self._set_layouts()


    def _set_labels(self):

        self.online_music = QLabel("在线音乐")
        self.online_music.setObjectName('online_music')
        self.online_music.setMaximumHeight(27)

        self.my_music = QLabel("我的音乐")
        self.my_music.setObjectName('my_music')
        self.my_music.setMaximumHeight(27)

        self.list_label = QLabel("创建的歌单")
        self.list_label.setObjectName("list_label")
        self.list_label.setMaximumHeight(27)

    def _set_buttons(self):
        ''' create a song list button '''
        self.create_list = QPushButton(self)
        # self.create_list.setIcon(QIcon('resource/add.png'))
        self.create_list.setObjectName('create_list_button')
        self.create_list.setMinimumSize(23, 23)
        self.create_list.setMaximumSize(23, 23)
        self.create_list.setStyle(QStyleFactory.create('Fusion'))
        self.create_list.setCursor(Qt.PointingHandCursor)

        self.create_list.clicked.connect(self._create_playlist)

    
    def _set_list_views(self):
        self.navigation_list = QListWidget()
        self.navigation_list.setMaximumHeight(160)
        self.navigation_list.setMaximumWidth(210)
        self.navigation_list.setObjectName('navigation_list')
        self.navigation_list.addItem(QListWidgetItem(QIcon('resource/qq_music.png'), "QQ音乐"))
        self.navigation_list.addItem(QListWidgetItem(QIcon('resource/netease_music.png'), '网易云音乐'))
        self.navigation_list.addItem(QListWidgetItem(QIcon('resource/migu.png'), '咪咕音乐'))
        self.navigation_list.itemClicked.connect(self._discover_music)
        # self.navigation_list.setCurrentRow(0)

        self.local_list = QListWidget()
        self.local_list.setObjectName('local_list')
        self.local_list.setMaximumHeight(100)
        self.local_list.setMaximumWidth(210)
        self.local_list.addItem(QListWidgetItem(QIcon('resource/local.png'), "本地音乐"))
        self.local_list.itemClicked.connect(self._local_music)

        self.play_list = QListWidget()
        self.play_list.setObjectName('play_list')
        self.play_list.setMaximumWidth(210)
        self.play_list.setMinimumHeight(300)
        # add song list
        for file_path in os.listdir('userdata/playlist'):
            list_name = file_path.split('.')[0]
            self.play_list.addItem(QListWidgetItem('  '+list_name))
            self.playlist_count += 1
      
        self.play_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.play_list.customContextMenuRequested.connect(self._playlist_right_menu)
        self.play_list.itemClicked.connect(self._music_list)
    

    def _discover_music(self):
        self.parent.main_list.display_mode = 'global'
        self.parent.main_list.music_list.clear()
        
        if self.navigation_list.currentRow() == 0:
            self.parent.header.music_source = 'qq'
        elif self.navigation_list.currentRow() == 1:
            self.parent.header.music_source = 'netease'
        elif self.navigation_list.currentRow() == 2:
            self.parent.header.music_source = 'migu'
        else:
            raise IndexError

        self.search_music_signal.emit()

        self.local_list.setCurrentItem(None)
        self.play_list.setCurrentItem(None)
    

    def _local_music(self):
        ''' display local music in main_list '''
        self.navigation_list.setCurrentItem(None)
        self.play_list.setCurrentItem(None)
        self.parent.main_list.music_list.clear()
        self.parent.main_list.display_mode = 'local'

        for file_path in os.listdir('userdata/music'):
            path = os.path.join('userdata/music', file_path)
            media_info = json.loads(MediaInfo.parse(path).to_json())['tracks'][0]

            # song_name = media_info['title'] if 'title' in media_info else file_path.split('_')[0]
            song_name = file_path.split('_')[0]
            singers = media_info['performer'] if 'performer' in media_info else ''
            album_name = media_info['album'] if 'album' in media_info else ''

            api = QQMusicApi()
            
            duration = convert_interval(
                math.floor(media_info['duration']/1000)) if 'duration' in media_info else ''
            
            song_mid = file_path.split('.')[0].split('_')[1]
            
            qt_item = QTreeWidgetItem()
            qt_item.setText(0, song_name)
            qt_item.setText(1, singers)
            qt_item.setText(2, album_name)
            qt_item.setText(3, duration)
            qt_item.setText(4, song_mid)
            
            self.parent.main_list.music_list.addTopLevelItem(qt_item)


    def _music_list(self):
        ''' display playlist in main_list '''
        self.navigation_list.setCurrentItem(None)
        self.local_list.setCurrentItem(None)
        self.parent.main_list.music_list.clear()
        self.parent.main_list.display_mode = 'list'

        item = self.play_list.currentItem()
        list_name = item.text().strip()

        song_list = [] # read from .json file 
        for file_path in os.listdir('userdata/playlist'):
            if list_name == file_path.split('.')[0]:
                with open(os.path.join('userdata/playlist', file_path), 'r') as f:
                    song_list = json.load(f)
                    break
        
        for song in song_list:
            qt_item = QTreeWidgetItem()
            qt_item.setText(0, song['song_name'])
            qt_item.setText(1, song['singers'])
            qt_item.setText(2, song['album_name'])
            qt_item.setText(3, song['interval'])
            qt_item.setText(4, song['song_mid'])
            qt_item.setText(5, song['url'])
            qt_item.setText(6, song['source'])

            self.parent.main_list.music_list.addTopLevelItem(qt_item)

    def _playlist_right_menu(self, pos):
        menu = QMenu(self.play_list)
        rename = menu.addAction("重命名")
        remove = menu.addAction("删除")

        action = menu.exec_(self.play_list.mapToGlobal(pos))
        item = self.play_list.currentItem()

        if action == rename:
            old_name = item.text()
            rename_line_edit = QLineEdit(old_name)
            self.play_list.setItemWidget(item, rename_line_edit)
            rename_line_edit.setFocus()
            rename_line_edit.returnPressed.connect(lambda: self.__rename_playlist(item, rename_line_edit, old_name))
            rename_line_edit.editingFinished.connect(lambda: self.__rename_playlist(item, rename_line_edit, old_name))
        elif action == remove:

    
    def __rename_playlist(self, item, rename_line_edit, old_name):
        new_name = rename_line_edit.text()
        for file_path in os.listdir('userdata/playlist'):
            if new_name == file_path.split('.')[0]:
                new_name = old_name
                break
        
        self.play_list.removeItemWidget(item)
        item.setText('  '+new_name)
        if new_name != old_name:
            os.rename(
                'userdata/playlist/{}.json'.format(old_name), 
                'userdata/playlist/{}.json'.format(new_name))



    def _create_playlist(self):
        self.play_list.addItem(QListWidgetItem())
        new_item = self.play_list.item(self.playlist_count)

        self.index = 1
        for file_path in os.listdir('userdata/playlist'):
            name = file_path.split('.')[0]
            if name == '新建歌单{}'.format(index):
                self.index += 1

        new_line_edit = QLineEdit('新建歌单{}'.format(self.index))
        
        self.play_list.setItemWidget(new_item, new_line_edit)
        new_line_edit.setFocus()
        new_line_edit.returnPressed.connect(lambda: self.__new_playlist(new_item, new_line_edit))
        new_line_edit.editingFinished.connect(lambda: self.__new_playlist(new_item, new_line_edit))

    def __new_playlist(self, new_item, new_line_edit):
        playlist_name = new_line_edit.text()
        print(playlist_name)

        if playlist_name != '新建歌单{}'.format(self.index):
            for file_path in os.listdir('userdata/playlist'):
                if playlist_name == file_path.split('.')[0]:
                    playlist_name = '新建歌单{}'.format(self.index)
                    break

        self.play_list.removeItemWidget(new_item)
        new_item.setText('  '+playlist_name)
        self.playlist_count += 1

        # create json file
        with open('userdata/playlist/{}.json'.format(playlist_name), 'w') as f:
            f.write('[]')


    def _set_layouts(self):
        self.main_layout = QVBoxLayout(self.frame)
        self.main_layout.setSpacing(0)

        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(self.online_music)
        self.main_layout.addSpacing(15)
        self.main_layout.addWidget(self.navigation_list)
        self.main_layout.addSpacing(60)

        self.main_layout.addWidget(self.my_music)
        self.main_layout.addSpacing(15)
        self.main_layout.addWidget(self.local_list)
        self.main_layout.addSpacing(20)

        self.song_list_layout = QHBoxLayout()
        self.song_list_layout.addWidget(self.list_label)
        self.song_list_layout.addWidget(self.create_list)

        self.main_layout.addLayout(self.song_list_layout)
        self.main_layout.addSpacing(15)
        self.main_layout.addWidget(self.play_list)
        self.main_layout.addSpacing(1)

        self.main_layout.addStretch(1)
        self.setContentsMargins(0, 0, 0, 0)


class Mainlist(QScrollArea):    
    ''' song QTreeWidget 
    0: song_name
    1: singers
    2: album_name
    3: interval
    4: song_mid
    5: image_url 
    '''
    play_global_signal = pyqtSignal(QTreeWidgetItem, str, str)
    pause_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(Mainlist, self).__init__()
        self.parent = parent

        self.music_dir = 'userdata/music'
        self.root_dir = os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))).replace('\\', '/')

        self.display_mode = 'global' # or 'local' or 'list'

        self.setObjectName('main_list')
        self.setMinimumHeight(700)
        self._set_music_list()

        with open('qss/Mainlist.qss', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
        self._set_layouts()
        

    def _set_music_list(self):
        self.music_list = QTreeWidget()
        self.music_list.setObjectName('music_list')
        self.music_list.setMinimumWidth(self.width())
        self.music_list.setMinimumHeight(self.height())
        self.music_list.setRootIsDecorated(False)
        self.music_list.setFocusPolicy(Qt.NoFocus)
        
        self.music_list.headerItem().setText(0, "歌曲")
        self.music_list.headerItem().setText(1, "歌手")
        self.music_list.headerItem().setText(2, "专辑")
        self.music_list.headerItem().setText(3, "时长")

        for i in range(4):
            self.music_list.header().setSectionResizeMode(i, QHeaderView.Fixed)
        self.music_list.header().setSectionsMovable(False)

        self.music_list.setColumnWidth(0, 400)
        self.music_list.setColumnWidth(1, 300)
        self.music_list.setColumnWidth(2, 400)
        self.music_list.setColumnWidth(3, 100)
        # self.music_list.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)

        # load more
        self.load_page = 3 # load page
        self.load_more_threshold = 9
        self.music_list.verticalScrollBar().valueChanged.connect(lambda: Thread(target=self._load_more).start())

        # double clicked = download and play
        self.music_list.itemDoubleClicked.connect(lambda: Thread(
            target=self._play_music, 
            args=(self.music_list.currentItem(),)).start())

        # right button mouse menu
        self.music_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.music_list.customContextMenuRequested.connect(self._right_menu)

    
    def _right_menu(self, pos):
        if self.display_mode != 'global':
            return
        menu = QMenu(self.music_list)
        play = menu.addAction("播放")
        add_action = []
        _play_list = []

        self.play_list_dir = 'userdata/playlist'
        for file_path in os.listdir(self.play_list_dir):
            list_name = file_path.split('.')[0]
            _play_list.append(list_name)
            add_action.append(menu.addAction("添加到{}".format(list_name)))

        action = menu.exec_(self.music_list.mapToGlobal(pos))
        item = self.music_list.currentItem()

        if action == play:
            Thread(target=self._play_music, args=(item,)).start()

        elif action in add_action:
            # get music info dict
            music_info = {}
            music_info['source'] = self.parent.header.music_source
            music_info['song_name'] = item.text(0)
            music_info['singers'] = item.text(1)
            music_info['album_name'] = item.text(2)
            music_info['interval'] = item.text(3)
            music_info['song_mid'] = item.text(4)
            music_info['url'] = item.text(5)
            music_info['source'] = item.text(6)

            # get song list json file path
            list_name = _play_list[add_action.index(action)]
            list_path = os.path.join(self.play_list_dir, '{}.json'.format(list_name))

            with open(list_path, 'r') as f:
                song_list = json.load(f)
            song_list.append(music_info)

            with open(list_path, 'w') as f:
                json.dump(song_list, f, indent=1)

            print('Add {} success.'.format(music_info['song_name']))


    def _play_music(self, qtree_item):
        ''' double click or right mouse button to play music
        If local exists, find the local path,
        if not, download according to song mid
        '''

        # pause music player
        self.pause_signal.emit()
        self.parent.player.song_info.setText('加载中...')

        song_name = qtree_item.text(0)
        song_mid = qtree_item.text(4)
        source = qtree_item.text(6)

        local_exist = False
        for music_file in os.listdir(self.music_dir):
            if song_mid in music_file:
                music_path = os.path.join(self.music_dir, music_file)
                local_exist = True


        if not local_exist:
            if source == 'qq':
                api = QQMusicApi()
            elif source == 'netease':
                api = NeteaseCloudMusicAPI()
            
            if source != 'migu':
                url = api.get_url(song_mid)
                if url is None:
                    self.parent.player.song_info.setText('该歌曲需要vip')
                    return
            else: # if migu, qtreeitem.text(5) is url
                url = qtree_item.text(5) 
            music_path = 'userdata/music/{}_{}.m4a'.format(song_name, song_mid)
            urllib.request.urlretrieve(url, music_path)


        self.play_global_signal.emit(qtree_item, music_path, self.display_mode)



    def _load_more(self):
        ''' load more when scroll bar is scrolled to the bottom
        only when searching music and in qq music
        '''
        if self.display_mode == 'local' or self.parent.header.music_source != 'qq':
            return
  
        # scroll bar at end
        if self.music_list.verticalScrollBar().value() == self.load_more_threshold:
            keywords = self.parent.header.search_line.text()

            api = QQMusicApi()
            search_result = api.search(self.load_page, keywords)
            for item in search_result:
                qt_item = QTreeWidgetItem()

                qt_item.setText(0, item['song_name'])

                singers = ''
                for singer in item['singer_list']:
                    singers += singer
                    singers += '/'
                singers = singers.strip('/')
                qt_item.setText(1, singers)

                qt_item.setText(2, item['album_name'])
                qt_item.setText(3, convert_interval(item['interval']))
                qt_item.setText(4, str(item['song_mid']))
                qt_item.setText(5, item['image_url'])

                self.parent.main_list.music_list.addTopLevelItem(qt_item)
            
            self.load_page += 1
            self.load_more_threshold += 10


    def _set_layouts(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.music_list)
        self.setLayout(self.main_layout)
    


class PlayWidgets(QFrame):
    ''' Play button, song bar, volume adjustment
    QSlider Ref: https://blog.csdn.net/jia666666/article/details/81534588
    '''
    music_end_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(PlayWidgets, self).__init__()
        self.setObjectName('PlayWidgets')
        self.parent = parent

        self.player = QMediaPlayer()
        self.player.positionChanged.connect(self._player_pos_change)
        self.play_list = []
        self.current_music = None

        self.setMaximumWidth(1350)
        self.setMinimumWidth(1350)
        self.setMinimumHeight(100)

        with open('qss/playWidgets.qss', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

        self._set_buttons()
        self._set_labels()
        self._set_sliders()
        self._set_layouts()

    
    def _set_buttons(self):
        ''' previous, play, next button
        volume button (set to 0)
        play mode button   
        '''

        self.previous_button = QPushButton(self)
        self.previous_button.setObjectName('previous_button')
        self.previous_button.clicked.connect(self.__previous_song)
        self.previous_button.setCursor(Qt.PointingHandCursor)

        self.play_button = QPushButton(self)
        self.play_button.setObjectName('play_button')
        self.play_button.clicked.connect(self.play)
        self.play_button.setCursor(Qt.PointingHandCursor)

        self.pause_button = QPushButton(self)
        self.pause_button.setObjectName('pause_button')
        self.pause_button.clicked.connect(self.pause)
        # default
        self.pause_button.hide()
        self.pause_button.setCursor(Qt.PointingHandCursor)

        self.next_button = QPushButton(self)
        self.next_button.setObjectName('next_button')
        self.next_button.clicked.connect(self.__next_song)
        self.next_button.setCursor(Qt.PointingHandCursor)

        self.volume = QPushButton(self)
        self.volume.setObjectName('volume')
        self.volume.clicked.connect(self.__volume)
        self.volume.setCursor(Qt.PointingHandCursor)

        # set volume to 0
        self.no_volume = QPushButton(self)
        self.no_volume.setObjectName('no_volume')
        self.no_volume.hide()
        self.no_volume.clicked.connect(self.__no_volume)
        self.no_volume.setCursor(Qt.PointingHandCursor)

        # play mode
        self.single = QPushButton(self)
        self.single.setObjectName('single')
        self.single.hide()
        self.single.setToolTip('单曲循环')
        self.single.clicked.connect(self.__single_mode)
        self.single.setCursor(Qt.PointingHandCursor)

        self.repeat = QPushButton(self)
        self.repeat.setObjectName('repeat')
        self.repeat.setToolTip('列表循环')
        self.repeat.clicked.connect(self.__repeat_mode)
        self.repeat.setCursor(Qt.PointingHandCursor)

        self.shuffle = QPushButton(self)
        self.shuffle.setObjectName('shuffle')
        self.shuffle.hide()
        self.shuffle.setToolTip('随机播放')
        self.shuffle.clicked.connect(self.__shuffle_mode)
        self.shuffle.setCursor(Qt.PointingHandCursor)
    

    def _set_labels(self):
        ''' time label: current time and total time '''
        self.time = QLabel(self)
        self.time.setText('00:00/00:00')
        self.song_info = QLabel(self)
        self.song_info.setText('BowenMusic')
        # self.album_img = ImgLabel('resource/logo2.png', 90, 70)
        # self.song_info.setText('晴天-周杰伦')
    
    def _set_sliders(self):
        ''' song's progress bar '''
        self.slider = QSlider(self)
        self.slider.setObjectName('slider')
        # self.slider.setMinimumHeight(5)
        # self.slider.setMaximumHeight(5)
        self.slider.setMinimumWidth(1300)
        self.slider.setMaximumWidth(1300)

        self.slider.setRange(0, 1000)
        self.slider.setValue(0)
        self.slider.setOrientation(Qt.Horizontal)

        self.slider.sliderPressed.connect(self.__slider_pressed)
        self.slider.sliderReleased.connect(self.__slider_released)


        self.volume_slider = QSlider(self)
        self.volume_slider.setObjectName('volume_slider')
        self.volume_slider.setValue(50)
        self.volume_slider.setMinimumHeight(5)
        self.volume_slider.setOrientation(Qt.Horizontal)

        self.volume_slider.valueChanged.connect(self.__volume_changed)
    

    def _set_layouts(self):
        self.main_layout = QVBoxLayout()

        self.main_layout.addWidget(self.slider)

        self.down_layout = QHBoxLayout()
        # self.down_layout.addWidget(self.album_img)
        # self.down_layout.addSpacing(70)
        self.down_layout.addWidget(self.song_info)
        self.down_layout.addStretch(1)
        # self.down_layout.addSpacing(200)

        self.down_layout.addWidget(self.single)
        self.down_layout.addWidget(self.repeat)
        self.down_layout.addWidget(self.shuffle)

        self.down_layout.addWidget(self.previous_button)
        self.down_layout.addWidget(self.play_button)
        self.down_layout.addWidget(self.pause_button)
        self.down_layout.addWidget(self.next_button)

        self.down_layout.addWidget(self.volume)
        self.down_layout.addWidget(self.no_volume)
        self.down_layout.addWidget(self.volume_slider)

        self.down_layout.addStretch(1)
        # self.down_layout.addSpacing(100)
        self.down_layout.addWidget(self.time)

        # self.down_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.down_layout)
        self.setLayout(self.main_layout)


    def play_from_main_list(self, qtree_item, music_path, mode):
        ''' Get signal from main list and play music
        qtree_item - `QTreeWidgetItem`
        music_path - local path
        mode - 'global', 'local', 'list'
        '''
        self.play_mode = mode
        # button
        self.play_button.hide()
        self.pause_button.show()
        # play list clear
        self.play_list.clear()

        # set media for QMediaPlayer
        q_path = QUrl.fromLocalFile(music_path)
        self.player.setMedia(QMediaContent(q_path))

        media_info = json.loads(MediaInfo.parse(music_path).to_json())['tracks'][0] # to get song interval
        item_dict = {
            'song_name': qtree_item.text(0),
            'singers': qtree_item.text(1),
            'album_name': qtree_item.text(2),
            'interval': '',
            'song_mid': qtree_item.text(4),
            'url': qtree_item.text(5),
            'source': qtree_item.text(6)
        }
        self.current_music = item_dict # qtreewidgetiem

        # set play_list according to the mode
        if mode == 'global':
            self.play_list.append(self.current_music)
        elif mode == 'list' or mode == 'local':
            iterator = QTreeWidgetItemIterator(self.parent.main_list.music_list)
            while iterator.value():
                item = iterator.value()
                item_dict = {
                    'song_name': item.text(0),
                    'singers': item.text(1),
                    'album_name': item.text(2),
                    'interval': '',
                    'song_mid': item.text(4),
                    'url': item.text(5),
                    'source': item.text(6)
                }

                self.play_list.append(item_dict)
                iterator.__iadd__(1)

        self.order_play_list = self.play_list[:]
        # play
        self.play()
        # set song_info
        if self.current_music['singers'] != '':
            self.song_info.setText(self.current_music['song_name'] + '-' + self.current_music['singers'])
        else:
            self.song_info.setText(self.current_music['song_name'])
        # set total time
        media_info = json.loads(MediaInfo.parse(music_path).to_json())['tracks'][0]
        interval = convert_interval(math.floor(media_info['duration']/1000))
        self.time.setText(self.time.text().split('/')[0] + '/' + interval)


    def play(self):
        self.play_button.hide()
        self.pause_button.show()
        self.player.play()


    def pause(self):
        self.play_button.show()
        self.pause_button.hide()
        self.player.pause()


    def next_song(self, direction=None):
        ''' when current music play end, continue to next song '''
        
        if self.current_music == None:
            return

        index = self.play_list.index(self.current_music)
        # next song mid
        if direction == 'next' or direction is None:
            if index == len(self.play_list) - 1:
                next_song_dict = self.play_list[0]
            else:
                next_song_dict = self.play_list[index+1]
        elif direction == 'prev':
            if index == 0:
                next_song_dict = self.play_list[len(self.play_list)-1]
            else:
                next_song_dict = self.play_list[index-1]
        else:
            raise valueError('direction error.')


        self.pause()

        # if local exists
        for music_file in os.listdir('userdata/music'):
            if next_song_dict['song_mid'] in music_file:
                next_path = os.path.join('userdata/music', music_file)
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(next_path)))
                self.play()

                # get true interval
                media_info = json.loads(MediaInfo.parse(next_path).to_json())['tracks'][0]
                interval = convert_interval(math.floor(media_info['duration']/1000))

                # set song name, singer, interval display
                if next_song_dict['singers'] != '':
                    self.song_info.setText(next_song_dict['song_name']+'-'+next_song_dict['singers'])
                else:
                    self.song_info.setText(next_song_dict['song_name'])
                self.time.setText(self.time.text().split('/')[0]+'/'+interval)
                self.current_music = next_song_dict

                iterator = QTreeWidgetItemIterator(self.parent.main_list.music_list)
                while iterator.value():
                    item = iterator.value()
                    if item.text(4) == next_song_dict['song_mid']:
                        self.parent.main_list.music_list.setCurrentItem(item)
                        break
                    iterator.__iadd__(1)
                return

        # local not exists, download according to song mid
        if next_song_dict['source'] == 'migu':
            url = next_song_dict['url']
        elif next_song_dict['source'] == 'qq':
            url = QQMusicApi().get_url(next_song_dict['song_mid'])
        elif next_song_didct['source'] == 'netease':
            url = NeteaseCloudMusicAPI().get_url(next_song_dict['song_mid'])

        next_path = 'userdata/music/{}_{}.m4a'.format(next_song_dict['song_name'], next_song_dict['song_mid'])
        urllib.request.urlretrieve(url, next_path)
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(next_path)))
        self.play()

        # get true interval
        media_info = json.loads(MediaInfo.parse(next_path).to_json())['tracks'][0]
        interval = convert_interval(math.floor(media_info['duration']/1000))

        # set song name, singer, interval display
        if next_song_dict['singers'] != '':
            self.song_info.setText(next_song_dict['song_name']+'-'+next_song_dict['singers'])
        else:
            self.song_info.setText(next_song_dict['song_name'])
        self.time.setText(self.time.text().split('/')[0]+'/'+interval)
        self.current_music = next_song_dict

        iterator = QTreeWidgetItemIterator(self.parent.main_list.music_list)
        while iterator.value():
            item = iterator.value()
            if item.text(4) == next_song_dict['song_mid']:
                self.parent.main_list.music_list.setCurrentItem(item)
                break
            iterator.__iadd__(1)


    def _player_pos_change(self):
        ''' when player position is changing, change slider and time info '''
        # current music total time (ms)
        if self.player.duration() == 0:
            return

        current_time = self.player.position() // 1000 # ms -> s
        api = QQMusicApi()
        total_time = self.time.text().split('/')[-1]

        # set time_info and slider
        self.time.setText(
            convert_interval(current_time)+'/'+total_time)
        self.slider.setValue(
            current_time/(self.player.duration()//1000) * 1000)
        
        if self.player.duration() == self.player.position():
            self.music_end_signal.emit()


    def __previous_song(self):
        ''' push previous button '''
        self.next_song('prev')

    def __next_song(self):
        ''' push next button '''
        self.next_song('next')

    def __volume(self):
        ''' volume to 0 '''
        self.volume.hide()
        self.no_volume.show()
        self.last_volume_value = self.volume_slider.value()
        self.volume_slider.setValue(0)

    def __no_volume(self):
        ''' open volume '''
        self.volume.show()
        self.no_volume.hide()
        self.volume_slider.setValue(self.last_volume_value)

    ''' Play mode setting functions
    ref: https://doc.qt.io/qt-5/qmediaplaylist.html#PlaybackMode-enum '''
    def __single_mode(self):
        ''' change to shuffle '''
        self.single.hide()
        self.shuffle.show()
        
        if self.current_music is None:
            return

        self.play_list = self.order_play_list[:]
        random.shuffle(self.play_list)


    def __repeat_mode(self):
        ''' change to single '''
        self.repeat.hide()
        self.single.show()
        
        if self.current_music is None:
            return

        index = self.play_list.index(self.current_music)
        self.play_list = [self.current_music]

    def __shuffle_mode(self):
        ''' change to repeat '''
        # print('change to repeat')
        self.shuffle.hide()
        self.repeat.show()

        if self.current_music is None:
            return
        
        self.play_list = self.order_play_list[:]

    def __slider_pressed(self):
        ''' Press slider (only once) '''
        self.player.positionChanged.disconnect()
        self.slider.sliderMoved.connect(self.__slider_moved)
    
    def __slider_moved(self):
        ''' moving slider '''
        ratio = self.slider.value() / 1000
        music_time = (self.player.duration() // 1000) * ratio # ms -> s
        music_time_str = convert_interval(int(music_time))
        
        total_time = self.time.text().split('/')[-1]
        self.time.setText(music_time_str + '/' + total_time)
        # self.player.setPosition(self.player.duration()*ratio)

    def __slider_released(self):
        ''' release slider '''
        ratio = self.slider.value() / 1000
        self.player.setPosition(self.player.duration()*ratio)
        self.player.positionChanged.connect(self._player_pos_change)
        self.slider.sliderMoved.disconnect()

    def __volume_changed(self):
        self.player.setVolume(self.volume_slider.value())
        if self.volume_slider.value() == 0:
            self.no_volume.show()
            self.volume.hide()
        else:
            self.no_volume.hide()
            self.volume.show()


    # def __add_music(self):
    #     local_url = 'D:/Bowen/SJTU/大三下/course/应用软件设计/Music/music/告白气球.m4a'
    #     q_url = QUrl.fromLocalFile(local_url)

    #     self.play_list.addMedia(QMediaContent(q_url))
    #     self.player.setPlaylist(self.play_list)
    #     self.player.play()

'''
app = QApplication(sys.argv)
play = Mainlist()
play.show()
sys.exit(app.exec_())
'''
