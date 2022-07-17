from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import os
import cv2


class VideoWidget(QWidget):
    path = None
    mediaPlayer = None
    placeholderLBL = None
    timeline = None

    mediaLoadedSignal = pyqtSignal(str)

    def __init__(self, timeline, path=None):
        super(VideoWidget, self).__init__()
        self.path = path

        self.placeholderLBL = QLabel("Drag file or click", self)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.view.setBackgroundBrush(QBrush(Qt.GlobalColor.black))
        self.view.setEnabled(False)
        self.view.hide()
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.videoItem = QGraphicsVideoItem()
        self.scene.addItem(self.videoItem)

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
        self.mediaPlayer.setVideoOutput(self.videoItem)
        self.mediaPlayer.setSource(QUrl.fromLocalFile(self.path))
        self.mediaPlayer.play()
        self.timeline.duration = self.getDuration()
        self.timeline.setFixedWidth(self.timeline.duration * self.timeline.scale)
        self.mediaPlayer.positionChanged.connect(self.timeline.setPlayheadPos)
        self.timeline.update()
        self.mediaLoadedSignal.emit(self.path)

        self.videoItem.setSize(self.videoItem.size())
        self.view.show()
        self.view.resize(self.size())

        self.resize(100, 100)
    
    def selectVideo(self):
        self.path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            os.path.abspath(os.sep),
            "Video files (*.mp4 *.mkv *.mov *.wmv)",
        )
        if self.path:
            self.initVideo()

    def resizeEvent(self, QResizeEvent):
        self.view.resize(self.size())
        videoRect = self.videoItem.boundingRect()

        rect = self.videoItem.boundingRect()

        self.view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

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
