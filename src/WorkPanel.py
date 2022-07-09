from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from SubtitleWidget import SubtitleWidget
import re
from datetime import datetime
import time

class WorkPanel(QWidget):
    subtitleWidgetList = []
    activeWidgetIndex = None
    subtitle = None
    video = None
    timeline = None

    def __init__(self, subtitle, video, timeline):
        super(WorkPanel, self).__init__()

        self.subtitle = subtitle
        self.video = video
        self.timeline = timeline

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.subtitleWidgetList = []

        self.show()

    def subSearch(self, pos): # milliseconds
        changed = False
        for sub in self.subtitleWidgetList:
            testStart = sub.validateTimestamp(sub.startTB)
            testEnd = sub.validateTimestamp(sub.endTB)
            if testStart and testEnd:
                start = sub.startTB.text()
                end = sub.endTB.text()
                if "." not in start:
                    start += ".00"
                if "." not in end:
                    end += ".00"
                start = (datetime.strptime(start, "%H:%M:%S.%f") -
                         datetime.strptime("00:00:00.00", "%H:%M:%S.%f")).total_seconds()
                end = (datetime.strptime(end, "%H:%M:%S.%f")-
                         datetime.strptime("00:00:00.00", "%H:%M:%S.%f")).total_seconds()
                if start <= pos / 1000 <= end:
                    self.subtitle.setText(sub.subtitleBodyTB.toPlainText())
                    self.subtitle.adjustSize()
                    self.subtitle.show()
                    changed = True
                    self.subtitle.move(self.video.width() / 2 - (self.subtitle.width() / 2),
                                       self.video.height() - self.subtitle.height() - 5)
                    break
        if not changed:
            self.subtitle.hide()

    def addSubtitle(self, start, end, body):
        newWidget = SubtitleWidget(len(self.subtitleWidgetList) + 1, start, end, body)
        newWidget.deleteSignal.connect(self.deleteSlot)
        newWidget.clickSignal.connect(self.clickSlot)
        newWidget.subtitleBodyTB.textChanged.connect(lambda: self.subSearch(self.video.mediaPlayer.position()))
        newWidget.startTB.textChanged.connect(self.timeline.update)
        newWidget.endTB.textChanged.connect(self.timeline.update)
        newWidget.deleteBTN.clicked.connect(lambda: self.subSearch(self.video.mediaPlayer.position()))
        self.layout.addWidget(newWidget)
        self.subtitleWidgetList.append(newWidget)

    def deleteSlot(self, sender):
        if self.activeWidgetIndex == None:
            cache = None
        else:
            cache = self.subtitleWidgetList[self.activeWidgetIndex]

        if self.subtitleWidgetList.index(sender) == self.activeWidgetIndex:
            self.activeWidgetIndex = None

        sender.setParent(None)
        self.subtitleWidgetList.remove(sender)

        for i in range(0, len(self.subtitleWidgetList)):
            self.subtitleWidgetList[i].numberLBL.setText(str(i + 1))
            if cache == self.subtitleWidgetList[i]:
                self.activeWidgetIndex = i

        if len(self.subtitleWidgetList) == 0:
            self.activeWidgetIndex = None

        self.timeline.update()

    def clickSlot(self, sender):
        if self.activeWidgetIndex is not None:
            if self.subtitleWidgetList[self.activeWidgetIndex] == sender:
                self.subtitleWidgetList[self.activeWidgetIndex].makeInactive()
                self.activeWidgetIndex = None
            else:
                self.subtitleWidgetList[self.activeWidgetIndex].makeInactive()
                self.activeWidgetIndex = self.subtitleWidgetList.index(sender)
                self.subtitleWidgetList[self.activeWidgetIndex].makeActive()
        else:
            self.activeWidgetIndex = self.subtitleWidgetList.index(sender)
            self.subtitleWidgetList[self.activeWidgetIndex].makeActive()