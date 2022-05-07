from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import math

class Timeline(QWidget):
    duration = None
    scale = 5
    scaleList = [0.1, 0.3, 0.5, 1, 2, 5, 10, 20]
    scaleIndex = 5
    clicking = False
    playheadPos = 0

    playheadChanged = pyqtSignal(int, float)

    def __init__(self):
        super(Timeline, self).__init__()
        
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedSize(0, 200)
        self.setStyleSheet("border: 0px;")

        self.show()

    def zoomIn(self):
        if self.scaleIndex < len(self.scaleList) - 1:
            intermediary = self.posToTime(self.playheadPos)
            self.scaleIndex += 1
            self.scale = self.scaleList[self.scaleIndex]
            self.setPlayheadPos(intermediary)
            self.setFixedSize(self.duration * self.scale, 200)
            self.update()

    def zoomOut(self):
        if self.scaleIndex > 0:
            intermediary = self.posToTime(self.playheadPos)
            self.scaleIndex -= 1
            self.scale = self.scaleList[self.scaleIndex]
            self.setPlayheadPos(intermediary)
            self.setFixedSize(self.duration * self.scale, 200)
            self.update()

    def setPlayheadPos(self, pos):
        pos = pos / 1000 * self.scale
        pos = pos - pos % self.scale
        if pos <= 0:
            self.playheadPos = 0
        elif pos >= self.duration * self.scale:
            self.playheadPos = self.duration * self.scale
        else:
            self.playheadPos = pos

    def posToTime(self, pos):
        return (pos / self.scale) * 1000

    def mousePressEvent(self, QMouseEvent):
        self.setPlayheadPos(self.posToTime(QMouseEvent.x()))
        self.update()
        self.playheadChanged.emit(self.playheadPos, self.scale)
        self.clicking = True

    def mouseMoveEvent(self, QMouseEvent):
        if self.clicking:
            self.setPlayheadPos(self.posToTime(QMouseEvent.x()))
            self.update()
            self.playheadChanged.emit(self.playheadPos, self.scale)

    def mouseReleaseEvent(self, QMouseEvent):
        self.clicking = False

    def paintEvent(self, QPaintEvent):
        painter = QPainter()
        painter.begin(self)

        timeFont = QFont()
        timeFont.setPixelSize(7)
        painter.setFont(timeFont)

        if self.scale >= 2:
            for i in range(1, int(self.duration) + 1):
                painter.drawLine(i * self.scale, 0, i * self.scale, 10)

        minutes = int(self.duration // 60)
        for i in range(1, minutes + 1):
            painter.drawLine(i * self.scale * 60, 0, i * self.scale * 60, 20)
            if self.scale >= 1:
                if i % 60 == 0:
                    pass
                elif i < 60:
                   painter.drawText(i * self.scale * 60 - 15, 27, "00:" + str(i).zfill(2) + ":00")
                else:
                    painter.drawText(i * self.scale * 60 - 15, 27, str(i // 60).zfill(2) + ":"
                                     + str(i - (60 * (i // 60))).zfill(2) + ":00")

        hours = int(self.duration // 3600)
        for i in range(1, hours + 1):
            painter.drawLine(i * self.scale * 3600, 0, i * self.scale * 3600, 30)
            painter.drawText(i * self.scale * 3600 - 15, 37, str(i).zfill(2) + "00:00")

        painter.drawLine(0, 40, self.width(), 40)

        painter.setPen(Qt.red)
        painter.setBrush(Qt.red)
        playheadPath = QPainterPath()
        playheadPath.moveTo(self.playheadPos, 10)
        playheadPath.lineTo(self.playheadPos - 5, 0)
        playheadPath.lineTo(self.playheadPos + 5, 0)
        playheadPath.lineTo(self.playheadPos, 10)
        playheadPath.lineTo(self.playheadPos, 200)
        painter.drawPath(playheadPath)

        painter.end()