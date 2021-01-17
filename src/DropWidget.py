# -*- coding: utf-8 -*-

from PySide2 import QtCore, QtWidgets


class DropWidget(QtWidgets.QFrame):

    dropped = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dragMoveEvent(self, e):
        if e.mimeData().hasUrls:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        if e.mimeData().hasUrls:
            e.setDropAction(QtCore.Qt.CopyAction)
            e.accept()

            for url in e.mimeData().urls():
                fname = str(url.toLocalFile())
                self.dropped.emit(fname)
        else:
            e.ignore()
