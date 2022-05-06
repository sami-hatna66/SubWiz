from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os

class VideoWidget(QVideoWidget):
    path = None
    mediaPlayer = None
    placeholderLBL = None

    def __init__(self, path = None):
        super(VideoWidget, self).__init__()
        self.path = path

        self.placeholderLBL = QLabel("Drag file or click", self)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.setAcceptDrops(True)

        self.show()

    def getDuration(self):
        if self.path is not None:
            return self.mediaPlayer.duration()
        else:
            return 0

    def setPath(self, newPath):
        self.path = newPath

    def initVideo(self):
        self.placeholderLBL.setParent(None)
        self.mediaPlayer.setVideoOutput(self)
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.path)))
        self.mediaPlayer.play()

    def mousePressEvent(self, QMouseEvent):
        if self.path is None:
            self.path, _ = QFileDialog.getOpenFileName(self,
                                                    "Open Video File",
                                                    os.path.abspath(os.sep),
                                                    "Video files (*.mp4 *.mkv *.mov *.wmv)")
            if self.path:
                self.initVideo()
            else:
                 self.path = None

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
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
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