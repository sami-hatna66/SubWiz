import os.path
from PyQt5.QtGui import QIcon, QMouseEvent, QCloseEvent
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QWidget, QHBoxLayout, QScrollArea, QVBoxLayout, QLabel, QPushButton, QMenuBar, QAction, QFileDialog, QApplication, QLineEdit
from PyQt5.QtCore import Qt, QEvent, QObject
from VideoWidget import VideoWidget
from Timeline import Timeline
from TopControl import TopControl
from BottomControl import BottomControl
from WorkPanel import WorkPanel
from WaveformWidget import WaveformWidget
from ExportWidget import ExportWidget
from ImportWidget import ImportWidget
import sys
from operator import itemgetter
from datetime import datetime


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Central widget
        self.centre = QWidget()
        self.setCentralWidget(self.centre)
        self.centreHBL = QHBoxLayout()
        self.centre.setLayout(self.centreHBL)

        # Contains video, top control, timeline and bottom control
        self.leftColumn = QWidget()
        # Contains work panel, import panel, add/delete buttons and waveform
        self.rightColumn = QWidget()

        # Container widget for video
        self.vidContainer = QWidget()
        self.vidContainer.setAttribute(Qt.WA_StyledBackground, True)
        self.vidContainer.setStyleSheet("background-color: #2D2E3B;")
        self.vidLayout = QVBoxLayout()
        self.vidLayout.setContentsMargins(0, 0, 0, 0)
        self.vidContainer.setLayout(self.vidLayout)

        self.timeline = Timeline()
 
        self.video = VideoWidget(self.timeline)
        
        self.waveformSA = QScrollArea()

        self.videoTimelineVBL = QVBoxLayout()
        self.leftColumn.setLayout(self.videoTimelineVBL)
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
        self.timelineSA.verticalScrollBar().setEnabled(False)
        self.timelineSA.verticalScrollBar().setStyleSheet("QScrollBar { height:0px; }")
        self.timelineSA.setStyleSheet("background-color: #2D2E3B;")
        self.videoTimelineVBL.addWidget(self.timelineSA)

        # Used for displaying subtitles over video widget
        self.subtitle = QLabel("", self.vidContainer)
        self.subtitle.hide()
        self.subtitle.setStyleSheet("color: white; background-color: black")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.workPanel = WorkPanel(self.subtitle, self.video, self.timeline)
        # Signal passes any space key presses up to play/pause function instead of calling on table
        self.workPanel.subtitleTable.spaceSignal.connect(
            self.topControl.playPauseAction
        )
        # Same for right and left arrow key press
        self.workPanel.subtitleTable.rightSignal.connect(
            lambda: self.topControl.forward(1)
        )
        self.workPanel.subtitleTable.leftSignal.connect(
            lambda: self.topControl.back(1)
        )
        # Move subtitle label back to bottom center when its size changes
        self.workPanel.adjustSubtitle.connect(self.adjustSubtitle)

        # Pass sorted and unsorted subtitle lists to timeline object
        self.timeline.passInSubtitles(
            self.workPanel.sortedSubtitleList, self.workPanel.subtitleList
        )

        self.waveformWidget = WaveformWidget(self.video)

        self.bottomControl = BottomControl(
            self.video,
            self.timelineSA,
            self.timeline,
            self.workPanel,
            self.waveformSA,
            self.waveformWidget
        )
        self.videoTimelineVBL.addWidget(self.bottomControl)

        # Add leftColumn to main layout
        self.centreHBL.addWidget(self.leftColumn, stretch=2)

        self.videoTimelineVBL.setSpacing(1)

        self.containerLayout = QVBoxLayout()
        self.rightColumn.setLayout(self.containerLayout)
        self.containerLayout.addWidget(self.workPanel)

        # Add rightColumn to main layout
        self.centreHBL.addWidget(self.rightColumn, stretch=1)

        self.importPanel = ImportWidget(self.workPanel)
        # Signal for when importing srt is done, connects to slot which hides import panel and show work panel
        self.importPanel.finishedImportSignal.connect(self.finishedImportSlot)
        self.containerLayout.addWidget(self.importPanel)
        # importPanel is hidden until user imports an srt file
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
        self.waveformSA.setStyleSheet("background-color: #2D2E3B;")
        self.waveformWidget.passInSubtitles(self.workPanel.sortedSubtitleList)
        # When a video file has been loaded in, start thread for generating its waveform
        self.video.mediaLoadedSignal.connect(self.waveformWidget.startWorker)
        self.waveformSA.setWidget(self.waveformWidget)
        self.containerLayout.addWidget(self.waveformSA)
        self.waveformSA.hide()

        self.mainMenu = QMenuBar(self)
        # File menu and actions
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

        # View menu and actions
        self.viewMenu = self.mainMenu.addMenu(" &View")

        self.showWaveformAction = QAction("Show Audio Waveform", self)
        self.showWaveformAction.triggered.connect(self.toggleWaveformVisibility)
        self.showWaveformAction.setEnabled(False)
        # showWaveformAction should only be enabled if a video has been loaded
        self.video.mediaLoadedSignal.connect(lambda: self.showWaveformAction.setEnabled(True))
        self.viewMenu.addAction(self.showWaveformAction)

        # Display subtitles for current position every time video position changes
        self.video.mediaPlayer.positionChanged.connect(self.workPanel.subSearch)

        self.installEventFilter(self)

        self.showMaximized()

        # ---------------------------------------------------------------------------------------------------------------
        self.video.setPath("/Users/sami/Downloads/hearttobreak.mp4")
        self.video.initVideo()
        # ---------------------------------------------------------------------------------------------------------------

        self.adjustSubtitle()

    # Select srt file and start import thread
    def importSRT(self):
        srtFilename, _ = QFileDialog.getOpenFileName(
            self, "Open SRT File", os.path.abspath(os.sep), "(*.srt)"
        )
        if srtFilename != "":
            self.workPanel.hide()
            self.addSubtitleBTN.hide()
            self.importPanel.show()

            self.importPanel.importFile(srtFilename)

    # Once srt is imported, load into data structures, hide import panel and show work panel
    # TODO move sorting code into thread
    def finishedImportSlot(self, newList):
        self.workPanel.subtitleList.clear()
        self.workPanel.sortedSubtitleList.clear()
        for sub in newList:
            sub.append(self.workPanel.idCounter)
            self.workPanel.subtitleList.append(sub)

            start = sub[0]
            end = sub[1]
            if "." not in start:
                start += ".00"
            if "." not in end:
                end += ".00"
            start = (
                datetime.strptime(start, "%H:%M:%S.%f")
                - datetime.strptime("00:00:00.00", "%H:%M:%S.%f")
            ).total_seconds()
            end = (
                datetime.strptime(end, "%H:%M:%S.%f")
                - datetime.strptime("00:00:00.00", "%H:%M:%S.%f")
            ).total_seconds()

            self.workPanel.sortedSubtitleList.append(
                [start * 1000, end * 1000, sub[2], self.workPanel.idCounter]
            )
            self.workPanel.idCounter += 1
        self.workPanel.sortedSubtitleList = sorted(
            self.workPanel.sortedSubtitleList, key=itemgetter(0)
        )
        self.workPanel.subtitleModel.layoutChanged.emit()
        self.workPanel.subtitleTable.changeRowHeights()
        self.importPanel.hide()
        self.workPanel.show()
        self.addSubtitleBTN.show()
        self.timeline.passInSubtitles(
            self.workPanel.sortedSubtitleList, self.workPanel.subtitleList
        )
        self.waveformWidget.passInSubtitles(self.workPanel.sortedSubtitleList)
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

    # Move subtitle label to bottom center of video widget
    def adjustSubtitle(self):
        self.subtitle.move(
            int(self.vidContainer.width() / 2 - (self.subtitle.width() / 2)),
            int(self.vidContainer.height() - self.subtitle.height() - 5),
        )

    # Fix subtitle label position any time window is resized
    def resizeEvent(self, QResizeEvent):
        self.adjustSubtitle()

    # If a video is loaded, space and arrow key presses should map to media control functions (unless a text box is active)
    def eventFilter(self, source: 'QObject', event: 'QEvent') -> bool:
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

    def mousePressEvent(self, event: QMouseEvent) -> None:
        focusedWidget = QApplication.focusWidget()
        if isinstance(focusedWidget, QLineEdit) or isinstance(focusedWidget, QTextEdit):
            focusedWidget.clearFocus()
        QMainWindow.mousePressEvent(self, event)

    def closeEvent(self, event: QCloseEvent) -> None:
        # Prevents segfault on close
        self.waveformWidget.worker.quit()
        self.video.mediaPlayer.stop()
        return super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(os.getcwd(), "assets", "SubwizIcon.png")))
    app.setApplicationName("Subwiz")
    root = MainWindow()
    root.setWindowTitle("Subwiz")
    # Apply stylesheet to all children of root
    with open(os.path.join(os.getcwd(), "stylesheet", "stylesheet.css"), "r") as ss:
        root.setStyleSheet(ss.read())
    root.show()
    sys.exit(app.exec())
