from os import times
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import re
from datetime import datetime
import time
from operator import itemgetter


def validateTimestampFormat(text):
    pattern = re.compile("^(2[0-3]|[0-1]?[\d]):[0-5][\d]:[0-5][\d](([:.])\d{1,3})?$")
    if pattern.search(text):
        return True
    elif text == "":
        return False
    else:
        return False


class InputBodyDelegate(QStyledItemDelegate):
    def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
        self.textEdit = QPlainTextEdit(QWidget)
        return self.textEdit

    def destroyEditor(self, QWidget, QModelIndex):
        return super().destroyEditor(QWidget, QModelIndex)


class InputTimeDelegate(QStyledItemDelegate):
    def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
        self.lineEdit = QLineEdit(QWidget)
        self.lineEdit.textChanged.connect(lambda: self.textChangedSlot(QModelIndex))
        return self.lineEdit

    def textChangedSlot(self, index):
        if index.column() < 2:
            if validateTimestampFormat(self.lineEdit.text()):
                self.lineEdit.setStyleSheet("background-color: #EBFFEB")
            elif self.lineEdit.text() == "":
                self.lineEdit.setStyleSheet("background-color: #FFFFFF")
            else:
                self.lineEdit.setStyleSheet("background-color: #FA867E")

    def destroyEditor(self, QWidget, QModelIndex):
        return super().destroyEditor(QWidget, QModelIndex)


class SubtitleTableModel(QAbstractTableModel):
    dataStore = None
    sortedDataStore = None
    headerLabels = ["Start", "End", "Body"]

    refreshRowHeights = pyqtSignal()
    receiveStoredDataStore = pyqtSignal()
    transmitSortedDataStore = pyqtSignal(list)
    refreshTimeline = pyqtSignal()

    def __init__(self, data, sortedData):
        super(SubtitleTableModel, self).__init__()
        self.dataStore = data
        self.sortedDataStore = sortedData

    def data(self, index: QModelIndex, role: int = ...):
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return self.dataStore[index.row()][index.column()]
        if role == Qt.ItemDataRole.BackgroundRole:
            if index.column() < 2:
                if validateTimestampFormat(self.dataStore[index.row()][index.column()]):
                    return QBrush(QColor("#EBFFEB"))
                elif self.dataStore[index.row()][index.column()] == "":
                    return QBrush(QColor("#FFFFFF"))
                else:
                    return QBrush(QColor("#FA867E"))
            else:
                return QBrush(QColor("#FFFFFF"))

    def setData(self, index: QModelIndex, value, role: int = ...):
        if role == Qt.ItemDataRole.EditRole:
            if index.row() < len(self.dataStore):
                self.dataStore[index.row()][index.column()] = value
                self.refreshRowHeights.emit()

                if index.column() < 2 and validateTimestampFormat(
                    self.dataStore[index.row()][index.column()]
                ):
                    self.receiveStoredDataStore.emit()
                    timestamp = self.dataStore[index.row()][index.column()]
                    if "." not in timestamp:
                        timestamp += ".00"
                    timeCount = (
                        datetime.strptime(timestamp, "%H:%M:%S.%f")
                        - datetime.strptime("00:00:00.00", "%H:%M:%S.%f")
                    ).total_seconds()
                    targetId = self.dataStore[index.row()][3]
                    self.sortedDataStore[
                        list(v[3] == targetId for v in self.sortedDataStore).index(True)
                    ][index.column()] = (timeCount * 1000)
                    if index.column() == 0:
                        self.sortedDataStore.sort(key=itemgetter(0), reverse=False)
                    self.refreshTimeline.emit()
                elif index.column() < 2:
                    self.receiveStoredDataStore.emit()
                    targetId = self.dataStore[index.row()][3]
                    self.sortedDataStore[
                        list(v[3] == targetId for v in self.sortedDataStore).index(True)
                    ][index.column()] = None
                    self.refreshTimeline.emit()
                else:
                    self.receiveStoredDataStore.emit()
                    targetId = self.dataStore[index.row()][3]
                    self.sortedDataStore[
                        list(v[3] == targetId for v in self.sortedDataStore).index(True)
                    ][index.column()] = value
                self.transmitSortedDataStore.emit(self.sortedDataStore)

            return True

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.dataStore)

    def columnCount(self, parent=None, *args, **kwargs):
        return 3

    def flags(self, index):
        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
        )

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return self.headerLabels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)


class SubtitleTable(QTableView):
    spaceSignal = pyqtSignal()
    leftSignal = pyqtSignal()
    rightSignal = pyqtSignal()

    def __init__(self):
        super(SubtitleTable, self).__init__()

    def changeRowHeights(self):
        for row in range(self.model().rowCount()):
            self.resizeRowToContents(row)
            self.setRowHeight(row, self.rowHeight(row) + 10)

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key.Key_Space:
            self.spaceSignal.emit()
        elif QKeyEvent.key() == Qt.Key.Key_Left:
            self.leftSignal.emit()
        elif QKeyEvent.key() == Qt.Key.Key_Right:
            self.rightSignal.emit()

    def mousePressEvent(self, QMouseEvent):
        clickedIndex = self.indexAt(QMouseEvent.pos())
        clickedRow = clickedIndex.row()

        if QMouseEvent.button() == Qt.MouseButton.RightButton:
            if len(self.selectionModel().selectedRows()) == 0 or clickedRow == -1:
                self.clearSelection()

            for index in self.selectionModel().selectedRows():
                if index.row() == clickedRow:
                    self.clearSelection()
                    return

            self.selectRow(clickedRow)

            self.setDisabled(True)
            self.setDisabled(False)

        elif QMouseEvent.button() == Qt.MouseButton.LeftButton:
            if clickedRow == -1:
                self.clearSelection()
            else:
                self.edit(clickedIndex)


class WorkPanel(QWidget):
    subtitleWidgetList = []
    activeWidgetIndex = None
    subtitle = None
    video = None
    timeline = None

    subtitleList = []

    adjustSubtitle = pyqtSignal()

    def __init__(self, subtitle, video, timeline):
        super(WorkPanel, self).__init__()

        self.subtitle = subtitle
        self.video = video
        self.timeline = timeline

        self.idCounter = 0

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        self.subtitleTable = SubtitleTable()
        self.subtitleTable.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.subtitleTable.horizontalHeader().setStretchLastSection(True)

        self.bodyDelegate = InputBodyDelegate()
        self.timeDelegate = InputTimeDelegate()
        self.subtitleTable.setItemDelegateForColumn(0, self.timeDelegate)
        self.subtitleTable.setItemDelegateForColumn(1, self.timeDelegate)
        self.subtitleTable.setItemDelegateForColumn(2, self.bodyDelegate)

        # start, end, body
        self.subtitleList = [
            ["00:00:00.000", "00:00:00.000", "Welcome to Subwiz!", self.idCounter]
        ]
        self.sortedSubtitleList = [[0, 0, "Welcome to Subwiz!", self.idCounter]]
        self.idCounter += 1

        self.subtitleModel = SubtitleTableModel(
            self.subtitleList, self.sortedSubtitleList
        )
        self.subtitleTable.setModel(self.subtitleModel)
        self.subtitleModel.refreshRowHeights.connect(
            self.subtitleTable.changeRowHeights
        )
        self.subtitleModel.transmitSortedDataStore.connect(self.reassignSortedData)
        self.subtitleModel.receiveStoredDataStore.connect(
            self.passSortedDataToModel, Qt.ConnectionType.DirectConnection
        )
        self.subtitleModel.refreshTimeline.connect(self.timeline.update)
        self.subtitleTable.changeRowHeights()

        self.layout.addWidget(self.subtitleTable)

        self.show()

        self.subtitleTable.setColumnWidth(0, self.subtitleTable.columnWidth(0) + 10)
        self.subtitleTable.setColumnWidth(1, self.subtitleTable.columnWidth(1) + 10)

    def reassignSortedData(self, newSortedData):
        self.sortedSubtitleList = newSortedData
        self.timeline.passInSubtitles(newSortedData, self.subtitleList)

    def passSortedDataToModel(self):
        self.subtitleModel.sortedDataStore = self.sortedSubtitleList

    def subSearch(self, pos):  # milliseconds
        changed = False
        for sub in self.sortedSubtitleList:
            start = sub[0]
            end = sub[1]
            if start != None and end != None:
                if start > pos and end > pos:
                    self.subtitle.hide()
                    break
                if start <= end:
                    if start <= pos <= end:
                        self.subtitle.setText(sub[2])
                        self.subtitle.show()
                        self.subtitle.adjustSize()
                        changed = True
                        self.adjustSubtitle.emit()
                        break
        if not changed:
            self.subtitle.hide()

    def addSubtitle(
        self, signalArtefact, start="00:00:00.000", end="00:00:00.000", body=""
    ):
        self.subtitleList.append([start, end, body, self.idCounter])
        self.sortedSubtitleList.insert(0, [0, 0, body, self.idCounter])
        self.idCounter += 1
        self.subtitleModel.layoutChanged.emit()
        self.subtitleTable.changeRowHeights()

        self.timeline.update()

    def deleteSubtitle(self):
        rows = []
        deletedIds = []
        for index in self.subtitleTable.selectionModel().selectedRows():
            rows.append(index.row())
            deletedIds.append(self.subtitleList[index.row()][3])
        for row in sorted(rows, reverse=True):
            del self.subtitleList[row]
        for id in deletedIds:
            self.sortedSubtitleList = [
                v for v in self.sortedSubtitleList if v[3] not in deletedIds
            ]
        self.subtitleModel.layoutChanged.emit()
        self.subtitleTable.changeRowHeights()
        self.timeline.passInSubtitles(self.sortedSubtitleList, self.subtitleList)

        self.timeline.update()
