from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from SubtitleWidget import SubtitleWidget

class WorkPanel(QWidget):
    def __init__(self):
        super(WorkPanel, self).__init__()

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.layout.addWidget(SubtitleWidget(1))

        self.show()