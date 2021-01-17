# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from DropWidget import DropWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(355, 174)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.watched_path_edit = QLineEdit(self.centralwidget)
        self.watched_path_edit.setObjectName(u"watched_path_edit")
        self.watched_path_edit.setGeometry(QRect(10, 30, 241, 20))
        self.watched_path_btn = QPushButton(self.centralwidget)
        self.watched_path_btn.setObjectName(u"watched_path_btn")
        self.watched_path_btn.setGeometry(QRect(260, 30, 61, 23))
        self.file_drop_area = DropWidget(self.centralwidget)
        self.file_drop_area.setObjectName(u"file_drop_area")
        self.file_drop_area.setGeometry(QRect(80, 60, 191, 61))
        self.file_drop_area.setFrameShape(QFrame.Box)
        self.file_drop_area.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.file_drop_area)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.file_drop_label = QLabel(self.file_drop_area)
        self.file_drop_label.setObjectName(u"file_drop_label")
        self.file_drop_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.file_drop_label)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 311, 16))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 355, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"GCode Uploader", None))
        self.watched_path_btn.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.file_drop_label.setText(QCoreApplication.translate("MainWindow", u"You can also drop\n"
"your Gcode files here !", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Select a directory to watch for incoming Gcode files:", None))
    # retranslateUi

