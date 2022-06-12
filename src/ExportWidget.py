from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os

class ExportWidget(QWidget):
    subtitleList = None
    exportPath = None

    def __init__(self, subtitleList):
        super(ExportWidget, self).__init__()

        self.subtitleList = subtitleList

        self.setAttribute(Qt.WA_QuitOnClose, False)

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Name:"), 0, 0)
        self.nameTB = QLineEdit()
        self.layout.addWidget(self.nameTB, 0, 1)

        self.layout.addWidget(QLabel("Location:"), 1, 0)
        self.locationBTN = QPushButton("Select location")
        self.locationBTN.setFixedWidth(150)
        self.locationBTN.clicked.connect(self.selectPath)
        self.layout.addWidget(self.locationBTN, 1, 1)

        self.layout.addWidget(QLabel("Filter Errors:"), 2, 0)
        self.filterErrors = QCheckBox()
        self.layout.addWidget(self.filterErrors, 2, 1)

        self.exportBTN = QPushButton("Export")
        self.exportBTN.clicked.connect(self.export)
        self.layout.addWidget(self.exportBTN, 3, 0, 1, 2)

        self.setWindowModality(Qt.ApplicationModal)
        self.show()

    def selectPath(self):
        filename = QFileDialog.getExistingDirectory(self, "Select Export Directory", os.path.abspath(os.sep))
        self.locationBTN.setText(filename)
        self.exportPath = filename

    def export(self):
        if self.nameTB.text() == "":
            self.nameTB.setStyleSheet("border: 1px solid red")
        elif self.exportPath is None:
            self.locationBTN.setStyleSheet("color: red")
        else:
            outputFile = open(self.exportPath + "/" + self.nameTB.text() + ".srt", "w")
            for sub in self.subtitleList:
                lines = [str(sub.numberLBL.text()) + "\n",
                         sub.startTB.text() + " --> " + sub.endTB.text() + "\n",
                         sub.subtitleBodyTB.toPlainText() + "\n",
                         "\n"]
                outputFile.writelines(lines)
            outputFile.close()
            self.close()