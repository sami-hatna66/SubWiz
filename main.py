from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from VideoWidget import VideoWidget
from Timeline import Timeline
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.centre = QWidget()
        self.setCentralWidget(self.centre)
        self.centreHBL = QHBoxLayout()
        self.centre.setLayout(self.centreHBL)

        self.videoTimelineVBL = QVBoxLayout()
        self.video = VideoWidget()
        self.videoTimelineVBL.addWidget(self.video)
        self.timelineSA = QScrollArea()
        self.timelineSA.setFocusPolicy(Qt.NoFocus)
        self.timelineSA.setWidgetResizable(True)
        self.timelineSA.setFixedHeight(210)
        self.timeline = Timeline()
        self.timelineSA.setWidget(self.timeline)
        self.videoTimelineVBL.addWidget(self.timelineSA)
        self.centreHBL.addLayout(self.videoTimelineVBL, stretch = 2)

        self.workPanel = QWidget()
        self.centreHBL.addWidget(self.workPanel, stretch = 1)

        self.showMaximized()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    root = MainWindow()
    root.show()
    sys.exit(app.exec())