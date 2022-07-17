import os.path
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from VideoWidget import VideoWidget
from Timeline import Timeline
from TopControl import TopControl
from BottomControl import BottomControl
from WorkPanel import WorkPanel
from WaveformWidget import WaveformWidget
from ExportWidget import ExportWidget
from ImportWidget import ImportWidget
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
        self.timelineSA.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.timelineSA.setWidgetResizable(True)
        self.timelineSA.setFixedHeight(210)
        self.timelineSA.setWidget(self.timeline)
        self.timelineSA.horizontalScrollBar().valueChanged.connect(self.timeline.update)
        self.videoTimelineVBL.addWidget(self.timelineSA)

        self.subtitle = QLabel("", self.vidContainer)
        self.subtitle.hide()
        self.subtitle.setStyleSheet("color: white; background-color: black")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.workPanel = WorkPanel(self.subtitle, self.video, self.timeline)
        self.workPanel.subtitleTable.spaceSignal.connect(
            self.topControl.playPauseAction
        )
        self.workPanel.subtitleTable.rightSignal.connect(
            lambda: self.topControl.forward(1)
        )
        self.workPanel.subtitleTable.leftSignal.connect(lambda: self.topControl.back(1))

        self.timeline.passInSubtitles(self.workPanel.subtitleList)

        self.bottomControl = BottomControl(
            self.video,
            self.timelineSA,
            self.timeline,
            self.workPanel,
            self.waveformSA,
        )
        self.videoTimelineVBL.addWidget(self.bottomControl)
        self.centreHBL.addLayout(self.videoTimelineVBL, stretch=2)

        self.videoTimelineVBL.setSpacing(1)

        self.containerLayout = QVBoxLayout()
        self.workSA = QScrollArea()
        self.workSA.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.workSA.setWidgetResizable(True)
        self.workSA.setWidget(self.workPanel)
        self.containerLayout.addWidget(self.workSA)
        self.centreHBL.addLayout(self.containerLayout, stretch=1)

        self.importPanel = ImportWidget(self.workPanel)
        self.importPanel.finishedImportSignal.connect(self.finishedImportSlot)
        self.containerLayout.addWidget(self.importPanel)
        self.importPanel.hide()

        self.addDeleteHBL = QHBoxLayout()

        self.addSubtitleBTN = QPushButton("Add Subtitle")
        self.addSubtitleBTN.clicked.connect(self.workPanel.addSubtitle)

        self.deleteSubtitleBTN = QPushButton("Delete Subtitle")
        self.deleteSubtitleBTN.clicked.connect(self.workPanel.deleteSubtitle)

        self.containerLayout.addLayout(self.addDeleteHBL)
        self.addDeleteHBL.addWidget(self.addSubtitleBTN)
        self.addDeleteHBL.addWidget(self.deleteSubtitleBTN)

        self.waveformSA.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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

        self.importNewVidAction = QAction("Import New Video File", self)
        self.importNewVidAction.triggered.connect(self.video.selectVideo)
        self.fileMenu.addAction(self.importNewVidAction)

        self.importSRTAction = QAction("Import SRT File", self)
        self.importSRTAction.triggered.connect(self.importSRT)
        self.fileMenu.addAction(self.importSRTAction)

        self.exportAction = QAction("Export SRT", self)
        self.exportAction.triggered.connect(self.exportSRT)
        self.fileMenu.addAction(self.exportAction)

        self.viewMenu = self.mainMenu.addMenu(" &View")

        self.showWaveformAction = QAction("Show Audio Waveform", self)
        self.showWaveformAction.triggered.connect(self.toggleWaveformVisibility)
        self.viewMenu.addAction(self.showWaveformAction)

        self.video.mediaPlayer.positionChanged.connect(self.workPanel.subSearch)

        self.installEventFilter(self)

        self.showMaximized()

        self.subtitle.move(
            self.vidContainer.width() / 2 - (self.subtitle.width() / 2),
            self.vidContainer.height() - self.subtitle.height() - 5,
        )

        # ---------------------------------------------------------------------------------------------------------------
        self.video.initVideo()
        self.video.setPath("/Users/sami/Downloads/Swiss Army Man.mp4")
        # ---------------------------------------------------------------------------------------------------------------

    def importSRT(self):
        srtFilename, _ = QFileDialog.getOpenFileName(
            self, "Open SRT File", os.path.abspath(os.sep), "(*.srt)"
        )
        if srtFilename != "":
            self.workSA.hide()
            self.addSubtitleBTN.hide()
            self.importPanel.show()

            self.importPanel.importFile(srtFilename)

    def finishedImportSlot(self, newList):
        self.workPanel.subtitleList.clear()
        for sub in newList:
            self.workPanel.subtitleList.append(sub)
        self.workPanel.subtitleModel.layoutChanged.emit()
        self.workPanel.subtitleTable.changeRowHeights()
        self.importPanel.hide()
        self.workSA.show()
        self.addSubtitleBTN.show()
        self.timeline.update()

    def exportSRT(self):
        self.exportWidget = ExportWidget(self.workPanel.subtitleList)

    def toggleWaveformVisibility(self):
        if self.waveformSA.isVisible():
            self.waveformSA.hide()
            self.showWaveformAction.setText("Show Audio Waveform")
        else:
            self.waveformSA.show()
            self.showWaveformAction.setText("Hide Audio Waveform")

    def resizeEvent(self, QResizeEvent):
        self.subtitle.move(
            self.vidContainer.width() / 2 - (self.subtitle.width() / 2),
            self.vidContainer.height() - self.subtitle.height(),
        )

    def eventFilter(self, source, event):
        if (
            event.type() == QEvent.Type.KeyPress
            and self.video.path is not None
            and source is self
        ):
            if event.key() == Qt.Key.Key_Space:
                self.topControl.playPauseAction()
            elif event.key() == Qt.Key.Key_Right:
                self.topControl.forward(1)
            elif event.key() == Qt.Key.Key_Left:
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
