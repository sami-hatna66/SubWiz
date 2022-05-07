from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class BottomControl(QWidget):
    timelineSA = None
    timeline = None
    video = None

    def __init__(self, video, timelineSA, timeline):
        super(BottomControl, self).__init__()

        self.timelineSA = timelineSA
        self.timeline = timeline
        self.video = video

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.markStartTimeBTN = QPushButton("Add Start Time")
        self.layout.addWidget(self.markStartTimeBTN)

        self.markEndTimeBTN = QPushButton("Add End Time")
        self.layout.addWidget(self.markEndTimeBTN)

        self.goToPlayheadBTN = QPushButton("Go To Playhead")
        self.goToPlayheadBTN.clicked.connect(self.goToPlayhead)
        self.layout.addWidget(self.goToPlayheadBTN)

        self.setFixedHeight(40)

    def goToPlayhead(self):
        self.timelineSA.horizontalScrollBar().setValue(int(
            self.timeline.playheadPos - (self.timelineSA.visibleRegion().boundingRect().width() / 2)
        ))