from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import timedelta

class ControlBar(QWidget):
    videoInstance = None
    isPaused = False
    duration = None

    def __init__(self, videoInstance):
        super(ControlBar, self).__init__()
        self.videoInstance = videoInstance

        self.layout = QHBoxLayout()
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0,0 ,0 ,0)
        self.setLayout(self.layout)

        self.backBTN = QPushButton("<")
        self.backBTN.clicked.connect(lambda: self.back(10))
        self.layout.addWidget(self.backBTN)

        self.playPauseBTN = QPushButton("Pause")
        self.playPauseBTN.clicked.connect(self.playPauseAction)
        self.layout.addWidget(self.playPauseBTN)

        self.forwardBTN = QPushButton(">")
        self.forwardBTN.clicked.connect(lambda: self.forward(10))
        self.layout.addWidget(self.forwardBTN)

        self.layout.addStretch()
        self.speedWidget = SpeedWidget(self.videoInstance)
        self.layout.addWidget(self.speedWidget)

        self.layout.addStretch()

        self.zoomInBTN = QPushButton("+")
        self.layout.addWidget(self.zoomInBTN)

        self.zoomOutBTN = QPushButton("-")
        self.layout.addWidget(self.zoomOutBTN)

        self.duration = str(timedelta(seconds=self.videoInstance.getDuration())).split(".")[0]
        self.timeStampLBL = QLabel("0:00:00 / " + self.duration)
        self.timeStampLBL.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self.timeStampLBL.setFixedSize(110, 20)
        self.layout.addWidget(self.timeStampLBL)

        self.videoInstance.mediaPlayer.positionChanged.connect(self.changeTimeStamp)

        self.setFixedHeight(40)

    def playPauseAction(self):
        if self.videoInstance.path is not None:
            if self.isPaused:
                self.videoInstance.mediaPlayer.play()
                self.playPauseBTN.setText("Pause")
                self.isPaused = False
            else:
                self.videoInstance.mediaPlayer.pause()
                self.playPauseBTN.setText("Play")
                self.isPaused = True

    def forward(self, amount):
        currentPos = self.videoInstance.mediaPlayer.position()
        if currentPos + (amount * 1000) >= self.videoInstance.getDuration() * 1000:
            self.videoInstance.mediaPlayer.setPosition(self.videoInstance.getDuration())
        else:
            self.videoInstance.mediaPlayer.setPosition(currentPos + (amount * 1000))

    def back(self, amount):
        currentPos = self.videoInstance.mediaPlayer.position()
        if currentPos - (amount * 1000) <= 0:
            self.videoInstance.mediaPlayer.setPosition(0)
        else:
            self.videoInstance.mediaPlayer.setPosition(currentPos - (amount * 1000))

    def changeTimeStamp(self, newTime):
        if self.duration == "0:00:00":
            self.duration = str(timedelta(seconds=self.videoInstance.getDuration() / 1000)).split(".")[0]
        self.timeStampLBL.setText(
            str(timedelta(seconds = newTime / 1000)).split(".")[0] + " / " + self.duration
        )

    def changeSpeed(self):
        self.buttonList[self.activeButtonIndex].setStyleSheet("color: black;")
        self.activeButtonIndex = self.buttonList.index(self.sender())
        self.buttonList[self.activeButtonIndex].setStyleSheet("color: red;")
        if self.videoInstance.path is not None:
            self.videoInstance.mediaPlayer.setPlaybackRate(self.speedList[self.activeButtonIndex])

class SpeedWidget(QWidget):
    videoInstance = None

    def __init__(self, videoInstance):
        super(SpeedWidget, self).__init__()

        self.videoInstance = videoInstance

        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.buttonList = []
        self.activeButtonIndex = 3
        self.speedList = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]

        for speed in self.speedList:
            temp = QPushButton(str(speed) + "x")
            temp.clicked.connect(self.changeSpeed)
            self.layout.addWidget(temp)
            self.buttonList.append(temp)

        self.buttonList[self.activeButtonIndex].setStyleSheet("color: red;")

        self.show()
        self.layout.setContentsMargins(0, 0, 0, 0)

    def changeSpeed(self):
        self.buttonList[self.activeButtonIndex].setStyleSheet("color: black;")
        self.activeButtonIndex = self.buttonList.index(self.sender())
        self.buttonList[self.activeButtonIndex].setStyleSheet("color: red;")
        if self.videoInstance.path is not None:
            self.videoInstance.mediaPlayer.setPlaybackRate(self.speedList[self.activeButtonIndex])