import json
import os
import sys
from cmd import Cmd

import mpv
from wcwidth import wcswidth
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api import MiguMusicAPI, NeteaseCloudMusicAPI, QQMusicApi, convert_interval


class MusicShell(Cmd):
    prompt = 'BowenMusic> '
    with open('src/cmd_version/intro.txt', 'r') as f:
        intro = f.read()


    def __init__(self):
        Cmd.__init__(self)
        self.playlist = list()
        self._get_playlist_info()
        self.api = NeteaseCloudMusicAPI()


    def _get_playlist_info(self):
        self.LIST_DIR = 'userdata/playlist'
        self.playlist.clear()
        for file_path in os.listdir(self.LIST_DIR):
            playlist_name = file_path.split('.')[0]
            self.playlist.append(playlist_name)


    
    def do_pl(self, arg):
        ''' show playlist 
        1. BowenMusic> pl          # all playlists overview
        2. BowenMusic> pl index    # show songs in index's playlist
        '''
        if arg == '':
            index = 1
            for index in range(len(self.playlist)):
                print('{}. {}'.format(index+1, self.playlist[index]))
        else:
            try:
                show_index = int(arg) - 1
                if show_index > len(self.playlist) - 1:
                    print('playlist index should smaller than {}.'.format(len(self.playlist)+1))
                    return
                print('\n歌单: {}'.format(self.playlist[show_index]))
                print('-'*15)
                print(' {:\u3000<14}{:\u3000<10}{:<}'.format('歌曲', '歌手', '专辑'))
                print('-'*70)
                with open(os.path.join(self.LIST_DIR, 
                    '{}.json'.format(self.playlist[show_index])), 'r') as f:
                    song_list = json.load(f)

                for index in range(len(song_list)):
                    print('{:2}. {:\u3000<12}{:\u3000<10}{:<}'.format(index+1, 
                        song_list[index]['song_name'], song_list[index]['singers'], song_list[index]['album_name']))
                print('-'*70)
            except:
                print('Args error.')


    def do_search(self, keyword):
        if self.api.name == 'qq':
            self.search_result = self.api.search(1, keyword)
            self._show_search()
        elif self.api.name == 'netease':
            self.search_result = self.api.search(keyword, 1)
            self._show_search()
        elif self.api.name == 'migu':
            self.search_result = self.api.search(keyword)
            self._show_search()
        else:
            print('api name not found.')
            return


    def _show_search(self):
        print('{}{}{}{}'.format(
            self._rpad('歌曲', 40), 
            self._rpad('歌手', 30), 
            self._rpad('专辑', 40), 
            self._rpad('时长', 40)))
        print('-'*120)
        index = 1
        for result in self.search_result:
            singer_list = result['singer_list']
            singers = ''
            for singer in singer_list:
                singers += singer+'/'
            singers = singers.strip('/')
            print('{}. {}{}{}{}'.format(
                index,
                self._rpad(result['song_name'], 40), 
                self._rpad(singers, 30),
                self._rpad(result['album_name'], 40), 
                self._rpad(convert_interval(result['interval']), 40)))
            index += 1
            if index == 11:
                break
        print('-'*120)

    def _lpad(self, text, length, padding=' '):
        return padding * max(0, (length-wcswidth(text))) + text
    def _rpad(self, text, length, padding=' '):
        return text + padding * max(0, (length-wcswidth(text)))

    def do_help(self, arg):
        pass

    # exit
    def do_quit(self, arg):
        print('Wish you good luck.')
        return True
    def do_bye(self, arg):
        return self.do_quit(arg)
    def do_exit(self, arg):
        return self.do_quit(arg)

    def default(self, arg):
        print('Command not defined, use help for more information.')



if __name__ == '__main__':
    MusicShell().cmdloop()
