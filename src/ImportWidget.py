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
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(sum(1 for line in open(path)))
        self.importWorker = ImportSRTThread(path)
        self.importWorker.addWidgetSignal.connect(self.workPanel.addSubtitle)
        self.importWorker.incrementProgressBarSignal.connect(self.incrementProgressBarSlot, Qt.BlockingQueuedConnection)
        self.importWorker.finishedImportSignal.connect(self.finishedImportSignal.emit)
        self.importWorker.start()

    def incrementProgressBarSlot(self):
        self.progressBar.setValue(self.progressBar.value() + 1)

class ImportSRTThread(QThread):
    path = None

    addWidgetSignal = pyqtSignal(str, str, str)
    incrementProgressBarSignal = pyqtSignal()
    finishedImportSignal = pyqtSignal()

    def __init__(self, path):
        super(ImportSRTThread, self).__init__()
        self.path = path

    def run(self):
        item = {}

        with open(self.path) as srtFile:
            prevLine = "number"
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
                        item["body"] = line

                elif line == "\n":
                    prevLine = "number"

                    self.addWidgetSignal.emit(item["start"], item["end"], item["body"])
                    self.incrementProgressBarSignal.emit()

                    item = {}

                time.sleep(0.01)

            self.finishedImportSignal.emit()
            self.quit()














