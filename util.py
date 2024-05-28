"""
Global constant values
Tool functions for MainWindow
"""

from PyQt5.QtWidgets import QListWidget, QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QColor as _QColor

VERSION = "0.2.3"

VIOLET = _QColor("#EE82EE")
GOLD = _QColor("#FFD700")

_STAR = "★"
THREESTAR = _STAR * 3
FOURSTAR = _STAR * 4
FIVESTAR = _STAR * 5
CH = "角色"
WP = "武器"

UNPATHED = "未定轨"


def writeRow(rowNum: int, row: list, table: QTableWidget, color=None):
    """
    Write or re-write a `row` of `rowNum`.
    """
    for i, cell in enumerate(row):
        table.setItem(rowNum, i, QTableWidgetItem(cell))
    if color:
        for i in range(table.columnCount()):
            table.item(rowNum, i).setBackground(color)


def readCols(indexs, table: QTableWidget):
    return [
        "".join((table.item(row, index).text() for index in indexs))
        for row in range(table.rowCount())
    ]


def filterCol(filterCol: int, targetCol: int, filterValue: str, table: QTableWidget):
    """
    In each row, if `filterCol` is `filterValue`, add `targetCol` of this row into list.
    """
    return [
        table.item(row, targetCol).text()
        for row in range(table.rowCount())
        if table.item(row, filterCol).text() == filterValue
    ]


def addRows(rows: list, table: QTableWidget, colors: list = None):
    currRowNum = table.rowCount()
    table.setRowCount(currRowNum + len(rows))
    if colors:
        for line, color in zip(rows, colors):
            writeRow(currRowNum, line, table, color)
            currRowNum += 1
    else:
        for line in rows:
            writeRow(currRowNum, line, table)
            currRowNum += 1
    table.scrollToBottom()


def addItems(rows: list, listw: QListWidget):
    listw.addItems(rows)
    listw.scrollToBottom()
