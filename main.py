from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from VideoWidget import VideoWidget
from Timeline import Timeline
from ControlBar import ControlBar, SpeedWidget
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
        #---------------------------------------------------------------------------------------------------------------
        self.video.setPath("/Users/sami/Downloads/Swiss Army Man.mp4")
        self.video.initVideo()
        #---------------------------------------------------------------------------------------------------------------
        self.videoTimelineVBL.addWidget(self.video)
        self.control = ControlBar(self.video)
        self.videoTimelineVBL.addWidget(self.control)
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