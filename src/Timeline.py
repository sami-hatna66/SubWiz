from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import math
from datetime import datetime
from WorkPanel import validateTimestampFormat


class Timeline(QWidget):
    duration = None
    scale = 5
    scaleList = [0.1, 0.3, 0.5, 1, 2, 5, 10, 20]
    scaleIndex = 5
    clicking = False
    playheadPos = 0

    subtitleList = None

    playheadChangedSignal = pyqtSignal(int, float)

    def __init__(self):
        super(Timeline, self).__init__()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setFixedSize(0, 200)
        self.setStyleSheet("border: 0px;")

        self.show()

    def passInSubtitles(self, subtitleList):
        self.subtitleList = subtitleList

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
        self.setPlayheadPos(self.posToTime(QMouseEvent.position().x()))
        self.update()
        self.playheadChangedSignal.emit(self.playheadPos, self.scale)
        self.clicking = True

    def mouseMoveEvent(self, QMouseEvent):
        if self.clicking:
            self.setPlayheadPos(self.posToTime(QMouseEvent.position().x()))
            self.update()
            self.playheadChangedSignal.emit(self.playheadPos, self.scale)

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
                    painter.drawText(
                        i * self.scale * 60 - 15, 27, "00:" + str(i).zfill(2) + ":00"
                    )
                else:
                    painter.drawText(
                        i * self.scale * 60 - 15,
                        27,
                        str(i // 60).zfill(2)
                        + ":"
                        + str(i - (60 * (i // 60))).zfill(2)
                        + ":00",
                    )

        hours = int(self.duration // 3600)
        for i in range(1, hours + 1):
            painter.drawLine(i * self.scale * 3600, 0, i * self.scale * 3600, 30)
            painter.drawText(i * self.scale * 3600 - 15, 37, str(i).zfill(2) + "00:00")

        maxTiers = (self.height() - 40) // 40
        data = []
        lanesData = []
        stack = [[0, 0, 0] for x in range(maxTiers)]
        colours = ["#FFFF00", "#0033CC", "#FF9900", "#00CC00", "#660099"]
        colourIndex = 0

        if self.subtitleList is not None:
            count = 0
            for sub in self.subtitleList:
                test1 = validateTimestampFormat(sub[0])
                test2 = validateTimestampFormat(sub[1])
                if test1 and test2:
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
                    if start != end:
                        data.append([start, end, count])
                count += 1

            for val in data:
                predicate = lambda d: d[1] <= val[0] and d[0] < val[0]
                try:
                    lane = stack.index(next(filter(predicate, stack), None))
                    yIndex = len(stack) if lane is None else lane
                except:
                    yIndex = 0
                lanesData.append([val, yIndex])
                stack[yIndex] = val

            for x in range(0, len(lanesData)):
                start = lanesData[x][0][0]
                end = lanesData[x][0][1]
                num = lanesData[x][0][2]
                lane = lanesData[x][1]
                painter.setPen(QPen(QColor(colours[colourIndex])))
                painter.setBrush(QBrush(QColor(colours[colourIndex])))
                painter.drawRect(
                    start * self.scale, 60 + (lane * 30), (end - start) * self.scale, 20
                )
                colourIndex = 0 if colourIndex >= len(colours) - 1 else colourIndex + 1
                painter.setPen(QPen(Qt.GlobalColor.black))
                font = QFont()
                font.setPointSize(15)
                painter.setFont(font)
                if self.scaleIndex > 4:
                    painter.drawText(
                        start * self.scale + 5, 75 + (lane * 30), str(num + 1)
                    )

        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.drawLine(0, 40, self.width(), 40)

        painter.setPen(Qt.GlobalColor.red)
        painter.setBrush(Qt.GlobalColor.red)
        playheadPath = QPainterPath()
        playheadPath.moveTo(self.playheadPos, 10)
        playheadPath.lineTo(self.playheadPos - 5, 0)
        playheadPath.lineTo(self.playheadPos + 5, 0)
        playheadPath.lineTo(self.playheadPos, 10)
        playheadPath.lineTo(self.playheadPos, 210)
        painter.drawPath(playheadPath)

        painter.end()
