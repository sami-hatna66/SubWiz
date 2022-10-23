import numpy as np
from PyQt5.QtGui import QPainter, QPen, QColor, QPaintEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from moviepy.editor import VideoFileClip


class WaveformWidget(QWidget):
    canDraw = False
    data = []
    playheadPos = 0
    video = None
    clicking = False

    def __init__(self, video):
        super(WaveformWidget, self).__init__()

        self.setFixedSize(200, 220)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: #2D2E3B; border: 0px;")

        self.video = video
        self.video.mediaPlayer.positionChanged.connect(self.setPlayheadPos)

        self.worker = AudioDataWorker(self.video.path)
        self.worker.completeSignal.connect(self.setAudioData)

    # Audio/video processing is done in separate thread
    def startWorker(self, newPath):
        self.canDraw = False
        self.update()
        self.worker.path = newPath
        self.worker.start()

    # Copy results of processing back to parent of thread ready to be painted
    def setAudioData(self, newData):
        self.data = newData
        if len(self.data) > 0:
            self.canDraw = True
            self.update()

    def setPlayheadPos(self, newPos):
        if len(self.data) > 0:
            self.playheadPos = newPos / 1000
            self.repaint()
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if self.canDraw:
            self.video.mediaPlayer.setPosition(int(event.x() * 1000))
            self.clicking = True
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.canDraw and self.clicking:
            self.video.mediaPlayer.setPosition(int(event.x() * 1000))
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.canDraw:
            self.clicking = False

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)

        if not self.canDraw:
            painter.setPen(QPen(Qt.white))
            painter.drawText(10, 110, "Generating Waveform...")
        else:
            visibleRegion = self.visibleRegion().boundingRect()
            # Paint audio waveform as a series of adjacent vertical lines
            painter.setPen(QPen(QColor("#61657E")))
            self.setFixedSize(len(self.data), 200)
            maxVal = max(self.data)
            for i in range(visibleRegion.x(), len(self.data)):
                if i <= visibleRegion.x() + visibleRegion.width():
                    lineStart = int(110 - ((self.data[i] * (200 / maxVal)) / 2))
                    lineEnd = int(110 + ((self.data[i] * (200 / maxVal)) / 2))
                    painter.drawLine(i, lineStart, i, lineEnd)
                else:
                    break
            # Draw playhead
            painter.setPen(QPen(Qt.GlobalColor.red))
            painter.drawLine(int(self.playheadPos), 0, int(self.playheadPos), 220)

        painter.end()


class AudioDataWorker(QThread):
    completeSignal = pyqtSignal(list)
    path = None

    def __init__(self, path):
        super(AudioDataWorker, self).__init__()
        self.path = path

    # Calculate amplitudes from video's audio data
    def run(self) -> None:
        clip = VideoFileClip(self.path)
        # Adjust segment size returned by cut based on overall audio duration
        # Longer audios should have larger segments to reduce processing time
        if (1 - (clip.audio.duration / 10000)) <= 0:
            offset = 0.1
        else:
            offset = 1 - (clip.audio.duration / 10000)
        # Cut segments of audio
        cut = lambda i: clip.audio.subclip(i, i + offset).to_soundarray(fps=22000)
        # Find average volume per segment
        volume = lambda array: np.sqrt(((1.0 * array) ** 2).mean())
        # Map lambdas onto data and store in list
        volumeList = [volume(cut(i)) for i in range(0, int(clip.audio.duration - 2))]

        self.completeSignal.emit(volumeList)
        self.quit()
