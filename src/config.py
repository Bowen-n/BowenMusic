import os
import sys
import time
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *

class ConfigHeader(QObject):

    def __init__(self, header):
        super(ConfigHeader, self).__init__()
        self.header = header

        self._bind_connect()

    
    def _bind_connect(self):
        self.header.close_button.clicked.connect(self.header.parent.close)
        self.header.min_button.clicked.connect(self.header.parent.showMinimized)

        