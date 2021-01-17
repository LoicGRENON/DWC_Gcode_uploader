# -*- coding: utf-8 -*-

from PySide2 import QtCore


def is_gcode_file(filename):
    file = QtCore.QFile(filename)
    suffix = QtCore.QFileInfo(file.fileName()).suffix()
    return suffix in ('gcode', 'g')
