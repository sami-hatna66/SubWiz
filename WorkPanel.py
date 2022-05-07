from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from SubtitleWidget import SubtitleWidget

class WorkPanel(QWidget):
    subtitleWidgetList = []
    activeWidgetIndex = None

    def __init__(self):
        super(WorkPanel, self).__init__()

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.subtitleWidgetList = []

        self.show()

    def addSubtitle(self):
        newWidget = SubtitleWidget(len(self.subtitleWidgetList) + 1)
        newWidget.deleteSignal.connect(self.deleteSlot)
        newWidget.clickSignal.connect(self.clickSlot)
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