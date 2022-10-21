from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QResizeEvent, QPixmap
from PyQt5.QtWidgets import QLabel, QFileDialog
from PyQt5.QtCore import pyqtSignal, Qt, QUrl, QSize
import os
import cv2


class VideoWidget(QVideoWidget):
    path = None
    mediaPlayer = None
    placeholderLBL = None
    timeline = None
    # OpenCV object holding current video
    # Used for extracting metadata not provided by Qt (e.g., dimensions, duration)
    vCap = None
    welcomeImg = None

    mediaLoadedSignal = pyqtSignal(str)

    def __init__(self, timeline, path=None):
        super(VideoWidget, self).__init__()
        # Assign arg to attribute
        self.path = path
        
        # If no video loaded, display welcome screen
        self.placeholderLBL = QLabel(self)
        self.welcomeImg = QPixmap(os.path.join(os.getcwd(), "assets", "welcomeScreen.png"))
        self.placeholderLBL.setPixmap(self.welcomeImg.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.mediaPlayer = QMediaPlayer(None)

        self.timeline = timeline
        # Change playback position whenever user does so via timeline
        self.timeline.playheadChangedSignal.connect(self.playheadChangedSlot)
        # Repaint timeline whenever playback position changes
        self.mediaPlayer.positionChanged.connect(self.timeline.update)

        # For drag-and-dropping video files
        self.setAcceptDrops(True)

        self.show()

    # Update media player position according to position clicked on timeline
    def playheadChangedSlot(self, position, scale):
        self.mediaPlayer.setPosition(int(position * 1000 / scale))

    # Get duration of video using OpenCV
    # (Qt doesn't seem to offer this functionality on its own)
    def getDuration(self):
        if self.path is not None:
            fps = self.vCap.get(cv2.CAP_PROP_FPS)
            frameTotal = self.vCap.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = float(frameTotal) / float(fps)
            return duration
        else:
            return 0

    def setPath(self, newPath):
        self.path = newPath

    def initVideo(self):
        # Pass new video into OpenCV object
        self.vCap = cv2.VideoCapture(self.path)
        # Clear welcome screen and display video
        self.placeholderLBL.setParent(None)
        self.mediaPlayer.setVideoOutput(self)
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.path)))
        self.mediaPlayer.play()
        # Adjust timeline for new video
        self.timeline.duration = self.getDuration()
        self.timeline.setFixedWidth(self.timeline.duration * self.timeline.scale)
        self.mediaPlayer.positionChanged.connect(self.timeline.setPlayheadPos)
        self.timeline.update()
        # Signal starts audio waveform generation
        self.mediaLoadedSignal.emit(self.path)
        self.resizeEvent(QResizeEvent(QSize(0, 0), QSize(self.width(), self.height())))

    def resizeEvent(self, event: QResizeEvent) -> None:
        if self.vCap is None:
            # Resize welcome screen to fit new widget size
            self.placeholderLBL.setPixmap(self.welcomeImg.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.placeholderLBL.resize(self.width(), self.height())
        else:
            # Resize video to get rid of black bars
            videoWidth = self.vCap.get(cv2.CAP_PROP_FRAME_WIDTH)
            videoHeight = self.vCap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            widgetWidth = self.width()
            widgetHeight = self.height()
            if widgetWidth > widgetHeight:
                ratio = widgetWidth / videoWidth
                self.setFixedHeight(ratio * videoHeight)
            else:
                ratio = widgetHeight / videoHeight
                self.setFixedWidth(ratio * videoWidth)

        return super().resizeEvent(event)

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

    # Recognise objects being dragged in
    def dragEnterEvent(self, event):
        self.setStyleSheet("border: 1px solid white;")
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("border: 0px;")

    # Recognise objects being dragged in
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    # Process files dropped in
    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
            results = []
            # Copy dragged path into program
            for url in event.mimeData().urls():
                results.append(str(url.toLocalFile()))
            Extension = os.path.splitext(results[0])[1]
            # Only accept video file formats
            acceptedExtensions = [".mp4", ".mkv", ".mov", ".wmv"]
            if Extension in acceptedExtensions:
                self.path = results[0]
                self.initVideo()
        else:
            event.ignore()
