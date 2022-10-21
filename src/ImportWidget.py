from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import pyqtSignal, QThread, Qt
import re


class ImportWidget(QWidget):
    path = None
    workPanel = None

    finishedImportSignal = pyqtSignal(list)

    def __init__(self, workPanel):
        super(ImportWidget, self).__init__()
        # Assign arg to attribute
        self.workPanel = workPanel

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Parsing SRT File..."))

        self.progressBar = QProgressBar()
        self.layout.addWidget(self.progressBar)

        self.show()

    # Thread will continually feed back to this class via incrementProgressBarSignal
    def importFile(self, path):
        self.progressBar.setValue(0)
        self.progressBar.setMaximum(sum(1 for line in open(path)))
        self.importWorker = ImportSRTThread(path)
        self.importWorker.incrementProgressBarSignal.connect(
            self.incrementProgressBarSlot, Qt.ConnectionType.BlockingQueuedConnection
        )
        self.importWorker.finishedImportSignal.connect(self.finishedImportSignal.emit)
        self.importWorker.start()

    def incrementProgressBarSlot(self):
        self.progressBar.setValue(self.progressBar.value() + 1)


class ImportSRTThread(QThread):
    path = None

    incrementProgressBarSignal = pyqtSignal()
    finishedImportSignal = pyqtSignal(list)

    def __init__(self, path):
        super(ImportSRTThread, self).__init__()
        self.path = path

    # Start asynchronous thread
    def run(self):
        data = []
        
        # Parse input srt file
        with open(self.path) as srtFile:
            prevLine = "number"
            # regex searches for timestamps
            timestampPattern = re.compile(
                "([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])([:,])\d{1,3} --> ([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])([:,])\d{1,3}"
            )

            # Follows format [Start, End, Text]
            item = []

            for line in srtFile:
                timestampSearch = timestampPattern.search(line)
                if timestampSearch:
                    prevLine = "timestamp"
                    item.append(timestampSearch.group(0)[0:12].replace(",", "."))
                    item.append(timestampSearch.group(0)[17:29].replace(",", "."))

                elif line != "\n" and (prevLine == "timestamp" or prevLine == "text"):
                    prevLine = "text"
                    if len(item) == 3:
                        item[2] += line
                    else:
                        item.append(line)

                elif line == "\n":
                    prevLine = "number"

                    item[2] = item[2].rstrip()

                    data.append(item)

                    item = []

                self.incrementProgressBarSignal.emit()

            if len(item) == 3:
                item[2] = item[2].rstrip()
                data.append(item)

            # Returns an unsorted list of subtitles, ready to be passed to table model in WorkPanel
            self.finishedImportSignal.emit(data)
            srtFile.close()
            self.quit()
