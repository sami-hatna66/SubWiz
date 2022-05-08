from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import re

class SubtitleWidget(QWidget):
    deleteSignal = pyqtSignal(QObject)
    clickSignal = pyqtSignal(QObject)

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
        self.startTB.textChanged.connect(lambda: self.validateTimestamp(self.startTB))
        self.timeHBL.addWidget(self.startTB)

        self.timeHBL.addWidget(QLabel("End:"))
        self.endTB = QLineEdit()
        self.endTB.textChanged.connect(lambda: self.validateTimestamp(self.endTB))
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
        self.deleteBTN.clicked.connect(lambda: self.deleteSignal.emit(self))
        self.layout.addWidget(self.deleteBTN)

        self.setFixedHeight(250)

        #qApp.installEventFilter(self)

        self.show()

    def validateTimestamp(self, sender):
        pattern = re.compile("^(2[0-3]|[0-1]?[\d]):[0-5][\d]:[0-5][\d](([:.])\d{1,3})?$")
        if pattern.search(sender.text()):
            sender.setStyleSheet("background-color: #EBFFEB")
        elif sender.text() == "":
            sender.setStyleSheet("background-color: white")
        else:
            sender.setStyleSheet("background-color: #FA867E")

    def eventFilter(self, source, event):
        if event.type() == event.FocusIn and (isinstance(source, QLineEdit) or isinstance(source, QTextEdit)):
            self.clickSignal.emit(self)
        return False

    def makeActive(self):
        self.activeLBL.show()

    def makeInactive(self):
        self.activeLBL.hide()

    def mousePressEvent(self, QMouseEvent):
        self.clickSignal.emit(self)
