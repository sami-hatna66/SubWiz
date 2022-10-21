from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QStyledItemDelegate, QPlainTextEdit, QLineEdit, QTableView, QWidget, QVBoxLayout, QAbstractItemView
from PyQt5.QtCore import QAbstractTableModel, pyqtSignal, QModelIndex, Qt
import re
from datetime import datetime
from operator import itemgetter

# Regex ensures string is a value timestamp format
def validateTimestampFormat(text):
    pattern = re.compile("^(2[0-3]|[0-1]?[\d]):[0-5][\d]:[0-5][\d](([:.])\d{1,3})?$")
    if pattern.search(text):
        return True
    else:
        return False


# Text editors which are shown when user edits any subtitle body cell in table
class InputBodyDelegate(QStyledItemDelegate):
    def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
        self.textEdit = QPlainTextEdit(QWidget)
        return self.textEdit

    def destroyEditor(self, QWidget, QModelIndex):
        return super().destroyEditor(QWidget, QModelIndex)


# Text editor which shows when user edits a timestamp cell in table
# Supports timestamp validation for contents
class InputTimeDelegate(QStyledItemDelegate):
    def createEditor(self, QWidget, QStyleOptionViewItem, QModelIndex):
        self.lineEdit = QLineEdit(QWidget)
        self.lineEdit.textChanged.connect(lambda: self.textChangedSlot(QModelIndex))
        return self.lineEdit

    def textChangedSlot(self, index):
        if index.column() < 2:
            # Color cell green if contents is a valid timestamp
            if validateTimestampFormat(self.lineEdit.text()):
                self.lineEdit.setStyleSheet("background-color: #305540")
            # No color if cell contains nothing
            elif self.lineEdit.text() == "":
                self.lineEdit.setStyleSheet("background-color: #2D2E3B")
            # Color cell red if contents is an invalid timestamp
            else:
                self.lineEdit.setStyleSheet("background-color: #850A3A")

    def destroyEditor(self, QWidget, QModelIndex):
        return super().destroyEditor(QWidget, QModelIndex)


# Table implementation conforms to Qt's Model View Architecture
class SubtitleTableModel(QAbstractTableModel):
    # Data items follow format [start, end, text, id]
    # dataStore stores times as timestamps whereas sortedDataStore stores them as no. of seconds
    # id links elements in sortedDataStore with elements in dataStore
    # sortedDataStore is used for efficient underlying search operations
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
        # Return contents of cell
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return self.dataStore[index.row()][index.column()]
        # Return color of cell
        if role == Qt.ItemDataRole.BackgroundRole:
            # Return results of timestamp validation for start and end columns
            if index.column() < 2:
                if validateTimestampFormat(self.dataStore[index.row()][index.column()]):
                    return QBrush(QColor("#305540"))
                elif self.dataStore[index.row()][index.column()] == "":
                    return QBrush(QColor("#2D2E3B"))
                else:
                    return QBrush(QColor("#850A3A"))
            # Any cell in text column always has same colour
            else:
                return QBrush(QColor("#2D2E3B"))
        if role == Qt.ItemDataRole.TextColorRole:
            return QBrush(QColor("#FFFFFF"))

    def setData(self, index: QModelIndex, value, role: int = ...):
        # Add new data to cells
        if role == Qt.ItemDataRole.EditRole:
            if index.row() < len(self.dataStore):
                # Assign new value to underlying data structure
                self.dataStore[index.row()][index.column()] = value
                self.refreshRowHeights.emit()

                # If new data is a valid timestamp, sortedDataStore must be re-sorted
                if index.column() < 2 and validateTimestampFormat(
                    self.dataStore[index.row()][index.column()]
                ):
                    # Most up-to-date version of sortedDataStore resides in WorkPanel instance
                    # Request up-to-date version as a precaution
                    self.receiveStoredDataStore.emit()
                    timestamp = self.dataStore[index.row()][index.column()]
                    if "." not in timestamp:
                        timestamp += ".00"
                    # Convert timestamp to seconds
                    timeCount = (
                        datetime.strptime(timestamp, "%H:%M:%S.%f")
                        - datetime.strptime("00:00:00.00", "%H:%M:%S.%f")
                    ).total_seconds()
                    # Find id in unsorted
                    targetId = self.dataStore[index.row()][3]
                    # Match id in sorted and assign new time 
                    self.sortedDataStore[
                        list(v[3] == targetId for v in self.sortedDataStore).index(True)
                    ][index.column()] = (timeCount * 1000)
                    # Sort sortedDataStore according to start values
                    if index.column() == 0:
                        self.sortedDataStore.sort(key=itemgetter(0), reverse=False)
                    # Update timeline to reflect changed timings
                    self.refreshTimeline.emit()
                # If the timestamp is invalid, it is added to sortedDataStore, but it doesn't need to be re-sorted
                elif index.column() < 2:
                    self.receiveStoredDataStore.emit()
                    targetId = self.dataStore[index.row()][3]
                    self.sortedDataStore[
                        list(v[3] == targetId for v in self.sortedDataStore).index(True)
                    ][index.column()] = None
                    self.refreshTimeline.emit()
                # If new data is subtitle text, add to both data stores, no sorting necessary
                else:
                    self.receiveStoredDataStore.emit()
                    targetId = self.dataStore[index.row()][3]
                    self.sortedDataStore[
                        list(v[3] == targetId for v in self.sortedDataStore).index(True)
                    ][index.column()] = value
                # Return new sortedDataStore to WorkPanel
                self.transmitSortedDataStore.emit(self.sortedDataStore)

        if role == Qt.ItemDataRole.TextColorRole:
            return QBrush(QColor("#FFFFFF"))

        return True

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.dataStore)

    def columnCount(self, parent=None, *args, **kwargs):
        return 3

    # Define table behaviour
    def flags(self, index):
        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
        )

    # For custom header labels
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return self.headerLabels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)


# View for SubtitleTableModel
class SubtitleTable(QTableView):
    spaceSignal = pyqtSignal()
    leftSignal = pyqtSignal()
    rightSignal = pyqtSignal()

    def __init__(self):
        super(SubtitleTable, self).__init__()

    # Adjust row heights to fit new contents
    def changeRowHeights(self):
        for row in range(self.model().rowCount()):
            self.resizeRowToContents(row)
            self.setRowHeight(row, self.rowHeight(row) + 10)

    # Propagate key press events upwards to main where they get reassigned to media control functions
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

        # A right click highlights row, marking it as ready for marking start and end times
        if QMouseEvent.button() == Qt.MouseButton.RightButton:
            # If click doesn't fall on any row, clear selection
            if len(self.selectionModel().selectedRows()) == 0 or clickedRow == -1:
                self.clearSelection()

            # Otherwise, select all right-clicked rows
            for index in self.selectionModel().selectedRows():
                if index.row() == clickedRow:
                    self.clearSelection()
                    return

            self.selectRow(clickedRow)

            self.setDisabled(True)
            self.setDisabled(False)

        # Left clicks open individual cells for editing
        elif QMouseEvent.button() == Qt.MouseButton.LeftButton:
            # If click doesn't fall on any row, clear selection
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
    sortedSubtitleList = []

    adjustSubtitle = pyqtSignal()

    def __init__(self, subtitle, video, timeline):
        super(WorkPanel, self).__init__()

        self.subtitle = subtitle
        self.video = video
        self.timeline = timeline

        # Keep track of unique assiged ids
        self.idCounter = 0

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create table and define behaviours
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

        # [start, end, text, id]
        self.subtitleList = [
            ["00:00:00.000", "00:00:00.000", "Welcome to Subwiz!", self.idCounter]
        ]
        # Times stored as total seconds in sorted list
        self.sortedSubtitleList = [[0, 0, "Welcome to Subwiz!", self.idCounter]]
        self.idCounter += 1

        # Initialise model which table conforms to
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

    # pos passed in as milliseconds
    def subSearch(self, pos):
        changed = False
        for sub in self.sortedSubtitleList:
            start = sub[0]
            end = sub[1]
            if start != None and end != None:
                # Discontinue search if start and end are both larger than current position
                # Can be done because list is sorted
                if start > pos and end > pos:
                    self.subtitle.hide()
                    break
                # Otherwise test if start is less than end and that pos lies between them both
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
        # Subtitles will default init with timestamps at 0 and no text
        self.subtitleList.append([start, end, body, self.idCounter])
        self.sortedSubtitleList.insert(0, [0, 0, body, self.idCounter])
        self.idCounter += 1
        # Re-sort subtitle list and reflect changes in SubtitleTable
        self.subtitleModel.layoutChanged.emit()
        self.subtitleTable.changeRowHeights()

        self.timeline.update()

    def deleteSubtitle(self):
        rows = []
        deletedIds = []
        # Get selected rows and their ids
        for index in self.subtitleTable.selectionModel().selectedRows():
            rows.append(index.row())
            deletedIds.append(self.subtitleList[index.row()][3])
        for row in sorted(rows, reverse=True):
            del self.subtitleList[row]
        # Delete same entries in sorted data structures, using id to match
        for id in deletedIds:
            self.sortedSubtitleList = [
                v for v in self.sortedSubtitleList if v[3] not in deletedIds
            ]
        # Re-sort subtitle list and reflect changes in SubtitleTable
        self.subtitleModel.layoutChanged.emit()
        self.subtitleTable.changeRowHeights()
        self.timeline.passInSubtitles(self.sortedSubtitleList, self.subtitleList)

        self.timeline.update()
