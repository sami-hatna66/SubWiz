from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from VideoWidget import VideoWidget
from Timeline import Timeline
from TopControl import TopControl
from BottomControl import BottomControl
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
        self.workPanel = WorkPanel()

        self.videoTimelineVBL = QVBoxLayout()
        #---------------------------------------------------------------------------------------------------------------
        self.video.setPath("/Users/sami/Downloads/Swiss Army Man.mp4")
        self.video.initVideo()
        #---------------------------------------------------------------------------------------------------------------
        self.videoTimelineVBL.addWidget(self.video)
        self.topControl = TopControl(self.video, self.timeline)
        self.videoTimelineVBL.addWidget(self.topControl)
        self.timelineSA = QScrollArea()
        self.timelineSA.setFocusPolicy(Qt.NoFocus)
        self.timelineSA.setWidgetResizable(True)
        self.timelineSA.setFixedHeight(210)
        self.timelineSA.setWidget(self.timeline)
        self.videoTimelineVBL.addWidget(self.timelineSA)

        self.bottomControl = BottomControl(self.video, self.timelineSA, self.timeline, self.workPanel)
        self.videoTimelineVBL.addWidget(self.bottomControl)
        self.centreHBL.addLayout(self.videoTimelineVBL, stretch = 2)

        self.videoTimelineVBL.setSpacing(1)

        self.containerLayout = QVBoxLayout()
        self.workSA = QScrollArea()
        self.workSA.setFocusPolicy(Qt.NoFocus)
        self.workSA.setWidgetResizable(True)
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
                self.topControl.playPauseAction()
            elif event.key() == Qt.Key_Right:
                self.topControl.forward(1)
            elif event.key() == Qt.Key_Left:
                self.topControl.back(1)
        return False

    def mousePressEvent(self, QMouseEvent):
        focusedWidget = QApplication.focusWidget()
        if isinstance(focusedWidget, QLineEdit) or isinstance(focusedWidget, QTextEdit):
            focusedWidget.clearFocus()
        QMainWindow.mousePressEvent(self, QMouseEvent)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    root = MainWindow()
    root.show()
    sys.exit(app.exec())