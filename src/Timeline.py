from PyQt5.QtGui import QPainter, QFont, QPen, QBrush, QColor, QPainterPath, QMouseEvent, QPaintEvent
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, Qt


class Timeline(QWidget):
    duration = None
    scale = 5
    scaleList = [0.1, 0.3, 0.5, 1, 2, 5, 10, 20]
    scaleIndex = 5
    clicking = False
    playheadPos = 0
    ctrlActive = False

    subtitleList = None
    unsortedSubtitleList = None

    # Connects to slot which changes media player position to new playhead position
    playheadChangedSignal = pyqtSignal(float, float)

    goToPlayheadSignal = pyqtSignal()

    def __init__(self):
        super(Timeline, self).__init__()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.setFixedSize(0, 200)
        self.setStyleSheet("border: 0px; background-color: #2D2E3B;")

        self.show()

    # timeline needs a reference to sorted and unsorted lists of subtitles from WorkPanel
    def passInSubtitles(self, subtitleList, unsortedSubtitleList):
        self.subtitleList = subtitleList
        self.unsortedSubtitleList = unsortedSubtitleList

    # Called by TopControl
    def zoomIn(self):
        if self.duration is not None and self.scaleIndex < len(self.scaleList) - 1:
            intermediary = self.posToTime(self.playheadPos)
            self.scaleIndex += 1
            self.scale = self.scaleList[self.scaleIndex]
            self.setPlayheadPos(intermediary)
            self.setFixedSize(int(self.duration * self.scale), 200)
            self.goToPlayheadSignal.emit()
            self.update()

    def zoomOut(self):
        if self.duration is not None and self.scaleIndex > 0:
            intermediary = self.posToTime(self.playheadPos)
            self.scaleIndex -= 1
            self.scale = self.scaleList[self.scaleIndex]
            self.setPlayheadPos(intermediary)
            self.setFixedSize(int(self.duration * self.scale), 200)
            self.goToPlayheadSignal.emit()
            self.update()
    
    def mediaTick(self, pos):
        self.setPlayheadPos(pos)
        self.update()

    def setPlayheadPos(self, pos):
        # Convert mouse press x position into time on timeline
        pos = pos / 1000 * self.scale
        # Press control to snap to second
        if self.ctrlActive:
            pos = pos - pos % self.scale
        if pos <= 0:
            self.playheadPos = 0
        elif pos >= self.duration * self.scale:
            self.playheadPos = self.duration * self.scale
        else:
            self.playheadPos = pos

    def posToTime(self, pos):
        return (pos / self.scale) * 1000

    # Click on timeline changes playback position
    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.setPlayheadPos(self.posToTime(event.x()))
        self.update()
        self.playheadChangedSignal.emit(float(self.playheadPos), self.scale)
        self.clicking = True

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.clicking:
            self.setPlayheadPos(self.posToTime(event.x()))
            self.update()
            self.playheadChangedSignal.emit(int(self.playheadPos), self.scale)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.clicking = False

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter()
        painter.begin(self)

        timeFont = QFont()
        timeFont.setPixelSize(10)
        painter.setFont(timeFont)
        painter.setPen(QPen(QColor("#8F8F8F")))

        # Draw second ticks
        if self.scale >= 2:
            for i in range(1, int(self.duration) + 1):
                painter.drawLine(int(i * self.scale), 0, int(i * self.scale), 10)

        # Draw minute ticks and timestamps
        minutes = int(self.duration // 60)
        for i in range(1, minutes + 1):
            painter.drawLine(int(i * self.scale * 60), 0, int(i * self.scale * 60), 20)
            if self.scale >= 1:
                if i % 60 == 0:
                    pass
                elif i < 60:
                    painter.drawText(
                        int(i * self.scale * 60 - 23), 30, "00:" + str(i).zfill(2) + ":00"
                    )
                else:
                    painter.drawText(
                        int(i * self.scale * 60 - 23),
                        30,
                        str(i // 60).zfill(2)
                        + ":"
                        + str(i - (60 * (i // 60))).zfill(2)
                        + ":00",
                    )

        # Draw hour ticks and timestamps
        hours = int(self.duration // 3600)
        for i in range(1, hours + 1):
            painter.drawLine(int(i * self.scale * 3600), 0, int(i * self.scale * 3600), 30)
            painter.drawText(int(i * self.scale * 3600 - 23), 43, str(i).zfill(2) + ":00:00")
        
        painter.drawLine(0, 48, self.width(), 48)

        maxTiers = (self.height() - 40) // 40
        data = []
        lanesData = []
        stack = [[0, 0, 0] for x in range(maxTiers)]
        # List of possible colours for timeline blocks
        colours = ["#9AA7E2", "#BEA6E6", "#796EA8", "#9568A2", "#634290"]
        # Loops around when all colours are used
        colourIndex = 0

        # Only render blocks visible in scroll area viewport
        visibleRegion = self.visibleRegion().boundingRect()

        if self.subtitleList is not None:
            count = 0
            for sub in self.subtitleList:
                if sub[0] != None and sub[1] != None:
                    start = sub[0] / 1000
                    end = sub[1] / 1000
                    if start != end and (
                        (
                            visibleRegion.x() - 50
                            <= start * self.scale
                            <= visibleRegion.x() + visibleRegion.width() + 50
                        )
                        or (
                            visibleRegion.x() - 50
                            <= end * self.scale
                            <= visibleRegion.x() + visibleRegion.width() + 50
                        )
                    ):
                        data.append([start, end, count, sub[3], colours[colourIndex]])
                        print(sub[3])
                        colourIndex = 0 if colourIndex >= len(colours) - 1 else colourIndex + 1
                    count += 1

            # Arrange overlapping subtitles into lanes
            for val in data:
                predicate = lambda d: d[1] <= val[0] and d[0] < val[0]
                try:
                    lane = stack.index(next(filter(predicate, stack), None))
                    yIndex = len(stack) if lane is None else lane
                except:
                    yIndex = 0
                lanesData.append([val, yIndex])
                stack[yIndex] = val

            # Change y offset from centre at which blocks are drawn according to how many lanes there are
            yOffset = 114
            if len(lanesData) > 0:
                maxLane = 0
                for sub in lanesData:
                    if maxLane == 2:
                        maxLane = 2
                        break
                    elif sub[1] > maxLane:
                        maxLane = sub[1]
                if maxLane == 1:
                    yOffset = 90
                elif maxLane == 2:
                    yOffset = 66

            # Draw subtitle blocks and number blocks
            for x in range(0, len(lanesData)):
                start = lanesData[x][0][0]
                end = lanesData[x][0][1]
                num = lanesData[x][0][2]
                id = lanesData[x][0][3]
                colour = lanesData[x][0][4]
                lane = lanesData[x][1]
                painter.setPen(QPen(QColor(colour)))
                painter.setBrush(QBrush(QColor(colour)))
                painter.drawRect(
                    int(start * self.scale),
                    int(yOffset + (lane * 30)),
                    int((end - start) * self.scale),
                    20,
                )
                painter.setPen(QPen(Qt.GlobalColor.black))
                font = QFont()
                font.setPointSize(15)
                painter.setFont(font)
                if self.scaleIndex > 4:
                    target = list(v[3] == id for v in self.unsortedSubtitleList).index(
                        True
                    )
                    painter.drawText(
                        int(start * self.scale + 5),
                        int(yOffset + 15 + (lane * 30)),
                        str(target + 1),
                    )

        # Draw playhead
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
