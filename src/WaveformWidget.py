import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from moviepy.editor import VideoFileClip, concatenate


class WaveformWidget(QWidget):
    canDraw = False
    data = []
    playheadPos = 0
    video = None

    def __init__(self, video):
        super(WaveformWidget, self).__init__()

        self.setFixedSize(200, 220)

        self.video = video
        self.video.mediaPlayer.positionChanged.connect(self.setPlayheadPos)

        self.worker = AudioDataWorker(self.video.path)
        self.worker.completeSignal.connect(self.setAudioData)

    def startWorker(self, newPath):
        self.worker.path = newPath
        self.worker.start()

    def setAudioData(self, newData):
        self.data = newData
        if len(self.data) > 0:
            self.canDraw = True
            self.update()

    def setPlayheadPos(self, newPos):
        if len(self.data) > 0:
            self.playheadPos = newPos / 1000
            self.repaint()

    def paintEvent(self, QPaintEvent):
        painter = QPainter()
        painter.begin(self)

        if not self.canDraw:
            painter.drawText(10, 110, "Generating Waveform")
        else:
            self.setFixedSize(len(self.data), 200)
            maxVal = max(self.data)
            for i in range(0, len(self.data)):
                lineStart = 110 - ((self.data[i] * (200 / maxVal)) / 2)
                lineEnd = 110 + ((self.data[i] * (200 / maxVal)) / 2)
                painter.drawLine(i, lineStart, i, lineEnd)
            painter.setPen(QPen(Qt.GlobalColor.red))
            painter.drawLine(self.playheadPos, 0, self.playheadPos, 220)

        painter.end()


class AudioDataWorker(QThread):
    completeSignal = pyqtSignal(list)
    path = None

    def __init__(self, path):
        super(AudioDataWorker, self).__init__()
        self.path = path

    def run(self):
        clip = VideoFileClip(self.path)
        if (1 - (clip.audio.duration / 10000)) <= 0:
            offset = 0.1
        else:
            offset = 1 - (clip.audio.duration / 10000)
        cut = lambda i: clip.audio.subclip(i, i + offset).to_soundarray(fps=22000)
        volume = lambda array: np.sqrt(((1.0 * array) ** 2).mean())
        volumeList = [volume(cut(i)) for i in range(0, int(clip.audio.duration - 2))]

        self.completeSignal.emit(volumeList)
