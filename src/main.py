from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from VideoWidget import VideoWidget
from Timeline import Timeline
from TopControl import TopControl
from BottomControl import BottomControl
from WorkPanel import WorkPanel
from WaveformWidget import WaveformWidget
from ExportWidget import ExportWidget
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.centre = QWidget()
        self.setCentralWidget(self.centre)
        self.centreHBL = QHBoxLayout()
        self.centre.setLayout(self.centreHBL)

        self.vidContainer = QWidget()
        self.vidLayout = QVBoxLayout()
        self.vidLayout.setContentsMargins(0, 0, 0, 0)
        self.vidContainer.setLayout(self.vidLayout)

        self.timeline = Timeline()
        self.video = VideoWidget(self.timeline)
        self.waveformSA = QScrollArea()

        self.videoTimelineVBL = QVBoxLayout()
        self.videoTimelineVBL.addWidget(self.vidContainer)
        self.vidLayout.addWidget(self.video)
        self.topControl = TopControl(self.video, self.timeline)
        self.videoTimelineVBL.addWidget(self.topControl)
        self.timelineSA = QScrollArea()
        self.timelineSA.setFocusPolicy(Qt.NoFocus)
        self.timelineSA.setWidgetResizable(True)
        self.timelineSA.setFixedHeight(210)
        self.timelineSA.setWidget(self.timeline)
        self.timelineSA.horizontalScrollBar().valueChanged.connect(self.timeline.update)
        self.videoTimelineVBL.addWidget(self.timelineSA)

        self.subtitle = QLabel("", self.vidContainer)
        self.subtitle.hide()
        self.subtitle.setStyleSheet("color: white; background-color: black")
        self.subtitle.setAlignment(Qt.AlignCenter)

        self.workPanel = WorkPanel(self.subtitle, self.video, self.timeline)

        self.timeline.passInSubtitles(self.workPanel.subtitleWidgetList)

        self.bottomControl = BottomControl(self.video, self.timelineSA, self.timeline, self.workPanel, self.waveformSA)
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

        self.waveformSA.setFocusPolicy(Qt.NoFocus)
        self.waveformSA.setWidgetResizable(True)
        self.waveformSA.setFixedHeight(220)
        self.waveformSA.verticalScrollBar().setStyleSheet("height: 0px;")
        self.waveformWidget = WaveformWidget(self.video)
        self.video.mediaLoadedSignal.connect(self.waveformWidget.startWorker)
        self.waveformSA.setWidget(self.waveformWidget)
        self.containerLayout.addWidget(self.waveformSA)
        self.waveformSA.hide()

        self.mainMenu = QMenuBar(self)

        self.fileMenu = self.mainMenu.addMenu(" &File")
        self.exportAction = QAction("Export SRT", self)
        self.exportAction.triggered.connect(self.exportSRT)
        self.fileMenu.addAction(self.exportAction)

        self.viewMenu = self.mainMenu.addMenu(" &View")
        self.showWaveformAction = QAction("Show Audio Waveform", self)
        self.showWaveformAction.triggered.connect(self.toggleWaveformVisibility)
        self.viewMenu.addAction(self.showWaveformAction)

        self.video.mediaPlayer.positionChanged.connect(self.workPanel.subSearch)

        qApp.installEventFilter(self)

        self.showMaximized()

        self.subtitle.move(self.vidContainer.width() / 2 - (self.subtitle.width() / 2),
                           self.vidContainer.height() - self.subtitle.height() - 5)

        #---------------------------------------------------------------------------------------------------------------
        self.video.setPath("/Users/sami/Downloads/Swiss Army Man.mp4")
        self.video.initVideo()
        #---------------------------------------------------------------------------------------------------------------

    def exportSRT(self):
        self.exportWidget = ExportWidget(self.workPanel.subtitleWidgetList)

    def toggleWaveformVisibility(self):
        if self.waveformSA.isVisible():
            self.waveformSA.hide()
            self.showWaveformAction.setText("Show Audio Waveform")
        else:
            self.waveformSA.show()
            self.showWaveformAction.setText("Hide Audio Waveform")

    def resizeEvent(self, QResizeEvent):
        self.subtitle.move(self.vidContainer.width() / 2 - (self.subtitle.width() / 2),
                           self.vidContainer.height() - self.subtitle.height())

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