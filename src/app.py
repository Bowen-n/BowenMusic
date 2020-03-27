import os
import sys
import time
from threading import Thread

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *

from module import Header, Mainlist, Navigation, PlayWidgets


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.setObjectName('MainWindow')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon('resource/logo.png'))
        self.setWindowTitle("BowenMusic")

        # self.resize(1050, 800)

        self.header = Header(self)
        self.navigation = Navigation(self)
        self.main_list = Mainlist(self)
        self.player = PlayWidgets(self)

        self.set_lines()
        self.set_layouts()
        self.config_signals()
        self.proper_place()

        with open('qss/window.qss', 'r') as f:
            self.setStyleSheet(f.read())

    
    def proper_place(self):
        screen = QDesktopWidget().screenGeometry()
        self.move(screen.width()*0.05, screen.height()*0.05)

    def set_lines(self):
        self.line1 = QFrame(self)
        self.line1.setObjectName('line1')
        self.line1.setFrameShape(QFrame.HLine)
        self.line1.setFrameShadow(QFrame.Plain)
        self.line1.setLineWidth(2)


    def set_layouts(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.addSpacing(5)
        self.main_layout.addWidget(self.header)
        self.main_layout.addSpacing(5)
        self.main_layout.addWidget(self.line1)

        self.content_layout = QHBoxLayout()
        # self.content_layout.setStretch(0, 200)
        # self.content_layout.setStretch(1, 800)
        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.addWidget(self.navigation)
        self.content_layout.addSpacing(10)

        self.list_and_player = QVBoxLayout()
        self.list_and_player.addWidget(self.main_list)
        self.list_and_player.addStretch(0)
        self.list_and_player.addWidget(self.player)

        self.content_layout.addLayout(self.list_and_player)

        self.main_layout.addLayout(self.content_layout)


        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)
    

    def config_signals(self):
        self.main_list.play_global_signal.connect(self.player.play_from_main_list, Qt.QueuedConnection)
        self.main_list.pause_signal.connect(self.player.pause, Qt.QueuedConnection)
        self.player.music_end_signal.connect(self.player.next_song)
        self.navigation.search_music_signal.connect(lambda: Thread(target=self.header.search).start(), Qt.QueuedConnection)


app = QApplication(sys.argv)
music = Window()
music.show()
sys.exit(app.exec_())
