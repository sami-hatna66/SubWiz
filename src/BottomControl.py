from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

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
        self.markStartTimeBTN.clicked.connect(self.timeline.update)
        self.layout.addWidget(self.markStartTimeBTN)

        self.markEndTimeBTN = QPushButton("Add End Time")
        self.markEndTimeBTN.clicked.connect(self.markEndTime)
        self.markEndTimeBTN.clicked.connect(self.timeline.update)
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

    @staticmethod
    def msecToTimeStamp(time):
        hrs = time // 3600000
        time = time - (3600000 * hrs)
        mins = time // 60000
        time = time - (60000 * mins)
        secs = time // 1000
        msecs = time - (1000 * secs)
        result = "{:d}:{:02d}:{:02d}.{:d}".format(hrs, mins, secs, msecs)
        return result

    def markStartTime(self):
        for index in self.workPanel.subtitleTable.selectionModel().selectedRows():
            self.workPanel.subtitleList[index.row()][0] = str(self.msecToTimeStamp(self.video.mediaPlayer.position()))
            self.workPanel.subtitleModel.setData(self.workPanel.subtitleList, Qt.ItemDataRole.DisplayRole)
            self.workPanel.subtitleTable.clearSelection()
            self.workPanel.subtitleTable.selectRow(index.row())

    def markEndTime(self):
        for index in self.workPanel.subtitleTable.selectionModel().selectedRows():
            self.workPanel.subtitleList[index.row()][1] = str(self.msecToTimeStamp(self.video.mediaPlayer.position()))
            self.workPanel.subtitleModel.setData(self.workPanel.subtitleList, Qt.ItemDataRole.DisplayRole)
            self.workPanel.subtitleTable.clearSelection()
            self.workPanel.subtitleTable.selectRow(index.row())