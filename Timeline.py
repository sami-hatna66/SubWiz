from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import math

class Timeline(QWidget):
    duration = None
    scale = 5
    scaleList = [0.1, 0.3, 0.5, 1, 2, 5, 10, 20]
    scaleIndex = 5
    clicking = False
    playHeadPos = 0

    def __init__(self):
        super(Timeline, self).__init__()
        
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedSize(0, 200)
        self.setStyleSheet("border: 0px;")