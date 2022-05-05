from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import math

class Timeline(QWidget):
    def __init__(self):
        super(Timeline, self).__init__()

        self.setFixedSize(10000, 200)