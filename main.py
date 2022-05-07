from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from VideoWidget import VideoWidget
from Timeline import Timeline
from ControlBar import ControlBar
from WorkPanel import WorkPanel
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.centre = QWidget()
        self.setCentralWidget(self.centre)
        self.centreHBL = QHBoxLayout()
        self.centre.setLayout(self.centreHBL)

        self.timeline = Timeline()
        self.video = VideoWidget(self.timeline)

        self.videoTimelineVBL = QVBoxLayout()
        #---------------------------------------------------------------------------------------------------------------
        self.video.setPath("/Users/sami/Downloads/Swiss Army Man.mp4")
        self.video.initVideo()
        #---------------------------------------------------------------------------------------------------------------
        self.videoTimelineVBL.addWidget(self.video)
        self.control = ControlBar(self.video, self.timeline)
        self.videoTimelineVBL.addWidget(self.control)
        self.timelineSA = QScrollArea()
        self.timelineSA.setFocusPolicy(Qt.NoFocus)
        self.timelineSA.setWidgetResizable(True)
        self.timelineSA.setFixedHeight(210)
        self.timelineSA.setWidget(self.timeline)
        self.videoTimelineVBL.addWidget(self.timelineSA)
        self.centreHBL.addLayout(self.videoTimelineVBL, stretch = 2)

        self.containerLayout = QVBoxLayout()
        self.workSA = QScrollArea()
        self.workSA.setWidgetResizable(True)
        self.workPanel = WorkPanel()
        self.workSA.setWidget(self.workPanel)
        self.containerLayout.addWidget(self.workSA)
        self.centreHBL.addLayout(self.containerLayout, stretch = 1)

        self.addSubtitleBTN = QPushButton("Add Subtitle")
        self.addSubtitleBTN.clicked.connect(self.workPanel.addSubtitle)
        self.containerLayout.addWidget(self.addSubtitleBTN)

        qApp.installEventFilter(self)

        self.showMaximized()

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and self.video.path is not None and source is self:
            if event.key() == Qt.Key_Space:
                self.control.playPauseAction()
            elif event.key() == Qt.Key_Right:
                self.control.forward(1)
            elif event.key() == Qt.Key_Left:
                self.control.back(1)
        return False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    root = MainWindow()
    root.show()
    sys.exit(app.exec())