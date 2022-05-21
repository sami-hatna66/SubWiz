from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class BottomControl(QWidget):
    timelineSA = None
    timeline = None
    video = None
    workPanel = None
    waveformSA = None

    def __init__(self, video, timelineSA, timeline, workPanel, waveformSA):
        super(BottomControl, self).__init__()

        self.timelineSA = timelineSA
        self.timeline = timeline
        self.video = video
        self.workPanel = workPanel
        self.waveformSA = waveformSA

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.markStartTimeBTN = QPushButton("Add Start Time")
        self.markStartTimeBTN.clicked.connect(self.markStartTime)
        self.layout.addWidget(self.markStartTimeBTN)

        self.markEndTimeBTN = QPushButton("Add End Time")
        self.markEndTimeBTN.clicked.connect(self.markEndTime)
        self.layout.addWidget(self.markEndTimeBTN)

        self.goToPlayheadBTN = QPushButton("Go To Playhead")
        self.goToPlayheadBTN.clicked.connect(self.goToPlayhead)
        self.layout.addWidget(self.goToPlayheadBTN)

        self.setFixedHeight(40)

    def goToPlayhead(self):
        self.timelineSA.horizontalScrollBar().setValue(int(
            self.timeline.playheadPos - (self.timelineSA.visibleRegion().boundingRect().width() / 2)
        ))
        self.waveformSA.horizontalScrollBar().setValue(int(
            (self.video.mediaPlayer.position() / 1000) - (self.waveformSA.visibleRegion().boundingRect().width() / 2)
        ))

    def msecToTimeStamp(self, time):
        hrs = time // 3600000
        time = time - (3600000 * hrs)
        mins = time // 60000
        time = time - (60000 * mins)
        secs = time // 1000
        msecs = time - (1000 * secs)
        result = "{:d}:{:02d}:{:02d}.{:d}".format(hrs, mins, secs, msecs)
        return result

    def markStartTime(self):
        if self.workPanel.activeWidgetIndex is not None:
            self.workPanel.subtitleWidgetList[self.workPanel.activeWidgetIndex].startTB.setText(
                str(self.msecToTimeStamp(self.video.mediaPlayer.position()))
            )

    def markEndTime(self):
        if self.workPanel.activeWidgetIndex is not None:
            self.workPanel.subtitleWidgetList[self.workPanel.activeWidgetIndex].endTB.setText(
                str(self.msecToTimeStamp(self.video.mediaPlayer.position()))
            )