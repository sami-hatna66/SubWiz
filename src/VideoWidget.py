from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os
import cv2


class VideoWidget(QVideoWidget):
    path = None
    mediaPlayer = None
    placeholderLBL = None
    timeline = None

    mediaLoadedSignal = pyqtSignal(str)

    def __init__(self, timeline, path=None):
        super(VideoWidget, self).__init__()
        self.path = path

        self.placeholderLBL = QLabel("Drag file or click", self)

        self.mediaPlayer = QMediaPlayer(None)

        self.timeline = timeline
        self.timeline.playheadChangedSignal.connect(self.playheadChangedSlot)
        self.mediaPlayer.positionChanged.connect(self.timeline.update)

        self.setAcceptDrops(True)

        self.show()

    def playheadChangedSlot(self, position, scale):
        self.mediaPlayer.setPosition(int(position * 1000 / scale))

    def getDuration(self):
        if self.path is not None:
            vCap = cv2.VideoCapture(self.path)
            fps = vCap.get(cv2.CAP_PROP_FPS)
            frameTotal = vCap.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = float(frameTotal) / float(fps)
            return duration
        else:
            return 0

    def setPath(self, newPath):
        self.path = newPath

    def initVideo(self):
        self.placeholderLBL.setParent(None)
        self.mediaPlayer.setVideoOutput(self)
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.path)))
        self.mediaPlayer.play()
        self.timeline.duration = self.getDuration()
        self.timeline.setFixedWidth(self.timeline.duration * self.timeline.scale)
        self.mediaPlayer.positionChanged.connect(self.timeline.setPlayheadPos)
        self.timeline.update()
        self.mediaLoadedSignal.emit(self.path)

    def selectVideo(self):
        self.path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            os.path.abspath(os.sep),
            "Video files (*.mp4 *.mkv *.mov *.wmv)",
        )
        if self.path:
            self.initVideo()

    def mousePressEvent(self, QMouseEvent):
        if self.path is None:
            self.selectVideo()

    def dragEnterEvent(self, event):
        self.setStyleSheet("border: 1px solid black")
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("border: 0px;")

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            results = []
            for url in event.mimeData().urls():
                results.append(str(url.toLocalFile()))
            Extension = os.path.splitext(results[0])[1]
            acceptedExtensions = [".mp4", ".mkv", ".mov", ".wmv"]
            if Extension in acceptedExtensions:
                self.path = results[0]
                self.initVideo()
        else:
            event.ignore()
