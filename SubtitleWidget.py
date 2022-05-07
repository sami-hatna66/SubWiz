from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class SubtitleWidget(QWidget):
    def __init__(self, number):
        super(SubtitleWidget, self).__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.numberLBL = QLabel(str(number))
        self.layout.addWidget(self.numberLBL)

        self.activeLBL = QLabel("Active")
        self.layout.addWidget(self.activeLBL)
        self.activeLBL.hide()

        self.timeHBL = QHBoxLayout()
        self.layout.addLayout(self.timeHBL)

        self.timeHBL.addWidget(QLabel("Start:"))
        self.startTB = QLineEdit()
        self.timeHBL.addWidget(self.startTB)

        self.timeHBL.addWidget(QLabel("End:"))
        self.endTB = QLineEdit()
        self.timeHBL.addWidget(self.endTB)

        self.formattingHBL = QHBoxLayout()
        self.boldBTN = QPushButton("B")
        self.formattingHBL.addWidget(self.boldBTN)
        self.italicBTN = QPushButton("I")
        self.formattingHBL.addWidget(self.italicBTN)
        self.underlineBTN = QPushButton("U")
        self.formattingHBL.addWidget(self.underlineBTN)
        self.layout.addLayout(self.formattingHBL)

        self.subtitleBodyTB = QTextEdit()
        self.layout.addWidget(self.subtitleBodyTB)

        self.deleteBTN = QPushButton("Delete")
        self.layout.addWidget(self.deleteBTN)

        self.setFixedHeight(250)

        self.show()



















