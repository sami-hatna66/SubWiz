from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
import re

class ImportWidget(QWidget):
    path = None
    workPanel = None

    finishedImportSignal = pyqtSignal()

    def __init__(self, workPanel):
        super(ImportWidget, self).__init__()
        self.workPanel = workPanel

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Parsing SRT File"))

        self.progressBar = QProgressBar()
        self.progressBar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        self.layout.addWidget(self.progressBar)

        self.show()

    def importFile(self, path):
        self.path = path

        fileLength = sum(1 for line in open(self.path))
        self.progressBar.setMaximum(2 * fileLength)

        fileData = []
        item = {}

        with open(self.path) as srtFile:
            prevLine = "text"
            timestampPattern = re.compile("([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])([:,])\d{1,3} --> ([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])([:,])\d{1,3}")

            for line in srtFile:
                timestampSearch = timestampPattern.search(line)
                if timestampSearch:
                    prevLine = "timestamp"
                    item["start"] = timestampSearch.group(0)[0:12].replace(",", ".")
                    item["end"] = timestampSearch.group(0)[17:29].replace(",", ".")

                elif line != "\n" and (prevLine == "timestamp" or prevLine == "text"):
                    prevLine = "text"
                    if "body" in item:
                        item["body"] += line
                    else:
                        item["body"] =  line

                elif line == "\n":
                    prevLine = "number"
                    fileData.append(item)
                    item = {}

                self.progressBar.setValue(self.progressBar.value() + 1)
                qApp.processEvents(QEventLoop.AllEvents, 50)

        for item in fileData:
            self.workPanel.addSubtitle()
            self.workPanel.subtitleWidgetList[-1].startTB.setText(item["start"])
            self.workPanel.subtitleWidgetList[-1].endTB.setText(item["end"])
            self.workPanel.subtitleWidgetList[-1].subtitleBodyTB.setText(item["body"])

            self.progressBar.setValue(self.progressBar.value() + 1)
            qApp.processEvents(QEventLoop.AllEvents, 50)

        print(fileData)

        self.finishedImportSignal.emit()

        # for x in range(0, 100):
        #     time.sleep(0.1)
        #     self.progressBar.setValue(self.progressBar.value() + 1)
        #     if not x % 20:
        #         qApp.processEvents(QEventLoop.AllEvents, 50)

