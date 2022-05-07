from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from SubtitleWidget import SubtitleWidget

class WorkPanel(QWidget):
    subtitleWidgetList = []
    index = 1

    def __init__(self):
        super(WorkPanel, self).__init__()

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.index = 1
        self.subtitleWidgetList = []

        self.show()

    def addSubtitle(self):
        newWidget = SubtitleWidget(self.index)
        newWidget.deleteSignal.connect(self.deleteSlot)
        self.layout.addWidget(newWidget)
        self.subtitleWidgetList.append(newWidget)
        self.index += 1

    def deleteSlot(self, sender):
        sender.setParent(None)
        self.subtitleWidgetList.remove(sender)

        self.index = 1
        for widget in self.subtitleWidgetList:
            widget.numberLBL.setText(str(self.index))
            self.index += 1