import os
import sys
import time
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *


class ImgLabel(QLabel):

    def __init__(self, src, width=200, height=200):
        super(ImgLabel, self).__init__()

        self.src = src
        self.width = width
        self.height = height

        self.setMaximumSize(self.width, self.height)
        self.setMinimumSize(self.width, self.height)

        self._set_img()


    def get_src(self):
        return self.src


    def _set_img(self):
        pic = QPixmap(self.src)
        pic.load(self.src)
        pic = pic.scaled(self.width, self.height)
        self.setPixmap(pic)

    

class SearchLineEdit(QLineEdit):

    def __init__(self, parent=None):
        super(SearchLineEdit, self).__init__()
        self.setObjectName("SearchLine")
        self.parent = parent
        self.setMinimumSize(280, 45)
        with open('qss/searchLine.qss', 'r') as f:
            self.setStyleSheet(f.read())

        self.button = QPushButton(self)
        self.button.setMaximumSize(20, 20)
        self.button.setCursor(QCursor(Qt.PointingHandCursor))

        self.setTextMargins(3, 0, 19, 0)
        self.spaceItem =  QSpacerItem(150, 10, QSizePolicy.Expanding)

        self.main_layout = QHBoxLayout()
        self.main_layout.addSpacerItem(self.spaceItem)
        self.main_layout.addWidget(self.button)
        self.main_layout.addSpacing(10)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)
    

    def set_button_slot(self, func):
        self.button.clicked.connect(func)


class ScrollLabel(QLabel):
    def __init__(self, parent=None):
        super(ScrollLabel, self).__init__()
        self.setObjectName("ScrollLabel")
        self.parent = parent
        self.text_len = self.fontMetrics().width(self.text())
    
    def setText(self, string):
        super().setText(string)
        self.text_len = self.fontMetrics().width(self.text())
        print(self.text_len)

    
