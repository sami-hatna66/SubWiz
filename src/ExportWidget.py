from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel, QLineEdit, QCheckBox, QFileDialog
from PyQt5.QtCore import Qt
import os
from WorkPanel import validateTimestampFormat


class ExportWidget(QWidget):
    subtitleList = None
    exportPath = None

    def __init__(self, subtitleList):
        super(ExportWidget, self).__init__()
        # Assign arg to attribute
        self.subtitleList = subtitleList

        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)

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
        self.filterErrors.setFixedSize(13, 13)
        self.layout.addWidget(self.filterErrors, 2, 1)

        self.exportBTN = QPushButton("Export")
        self.exportBTN.clicked.connect(self.export)
        self.layout.addWidget(self.exportBTN, 3, 0, 1, 2)

        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        with open(os.path.join(os.getcwd(), "stylesheet", "stylesheet.css"), "r") as ss:
            self.setStyleSheet(ss.read())

        self.setWindowFlags(
            Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowCloseButtonHint
        )

        self.show()

    # select path to export to via file explorer
    def selectPath(self):
        filename = QFileDialog.getExistingDirectory(
            self, "Select Export Directory", os.path.abspath(os.sep)
        )
        if filename != "":
            self.locationBTN.setText(filename)
            self.exportPath = filename

    def export(self):
        # If any required fields are blank, highlight to user and don't proceed
        if self.nameTB.text() == "":
            self.nameTB.setStyleSheet("border: 1px solid red")
        elif self.exportPath is None:
            self.locationBTN.setStyleSheet("color: red")
        else:
            outputFile = open(self.exportPath + "/" + self.nameTB.text() + ".srt", "w")
            for x in range(0, len(self.subtitleList)):
                # if filterErrors is checked, export will skip any subtitles with erroneous timestamps
                if (not self.filterErrors.isChecked()) or (
                    validateTimestampFormat(self.subtitleList[x][0])
                    and validateTimestampFormat(self.subtitleList[x][1])
                ):
                    lines = [
                        str(x + 1) + "\n",
                        self.subtitleList[x][0]
                        + " --> "
                        + self.subtitleList[x][1]
                        + "\n",
                        self.subtitleList[x][2] + "\n",
                        "\n",
                    ]
                    outputFile.writelines(lines)
            outputFile.close()
            self.close()
