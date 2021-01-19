# -*- coding: utf-8 -*-

import logging
from PySide2 import QtCore, QtNetwork, QtWidgets

from Config import Config
from FilePathWatcher import FilePathWatcher
from ui.main import Ui_MainWindow
from utils import is_gcode_file


class DWC_Gcode_uploader(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.config = Config()

        self.logger = logging.getLogger("app")
        self.__setup_logger()

        self.ui = Ui_MainWindow()
        self.__setup_ui()

        self.file_watcher = FilePathWatcher(self.config.watched_path)
        self.file_watcher.get_emitter().created_file_sig.connect(self.__on_new_gcode_file)
        self.__set_watching_path(self.config.watched_path)

        self._manager = QtNetwork.QNetworkAccessManager(self)
        self._manager.configuration().setConnectTimeout(3000)

        self.__del_localfile_after_upload = False
        self._is_uploading = False

        self.show()

    def __setup_logger(self):
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.setLevel(self.config.logging_level)

    def __setup_ui(self):
        self.ui.setupUi(self)

        self.ui.watched_path_btn.clicked.connect(self.__on_watched_path_btn_click)
        self.ui.file_drop_area.dropped.connect(self.__on_dropped_file)

    def __on_watched_path_btn_click(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        if dialog.exec_():
            filename = dialog.selectedFiles()[0]
            self.__set_watching_path(filename)

    def __on_dropped_file(self, filename):
        if self._is_uploading:
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
            error_dialog.setWindowTitle("Multiple upload not allowed")
            error_dialog.setText("An upload is already in progress. Please wait before uploading another file.")
            error_dialog.exec_()
            return False

        self.logger.debug(f"New file dropped: {filename}")

        if not is_gcode_file(filename):
            error_dialog = QtWidgets.QMessageBox()
            error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
            error_dialog.setWindowTitle("Incorrect filetype")
            error_dialog.setText("The file must be Gcode type (*.gcode, *.g).")
            error_dialog.exec_()
            return False

        self.__del_localfile_after_upload = False
        self.__upload_file(filename)

    def __set_watching_path(self, filepath):
        if not filepath:
            return

        self.logger.debug(f"Watching on {filepath}")
        self.ui.watched_path_edit.setText(filepath)
        self.file_watcher.change_path(filepath)
        self.file_watcher.start()

    def __on_new_gcode_file(self, file):
        # TODO: Throw a notification if an upload is already in progress (self._is_uploading is True)
        self.logger.debug(f"New Gcode file detected: {file}")
        self.__del_localfile_after_upload = self.config.delete_after_upload
        # TODO: Ensure the file is wrote before to send it
        # Crapy workaround using a timer
        QtCore.QTimer.singleShot(1000, lambda: self.__upload_file(file))

    def __upload_file(self, filename):
        # Prevents uploading multiple files at time
        if self._is_uploading:
            self.logger.debug("Multiple upload not permitted. Aborting.")
            return False

        file = QtCore.QFile(filename)
        file.open(QtCore.QFile.ReadOnly)

        gcode_name = QtCore.QFileInfo(file.fileName()).fileName()
        upload_uri = f'http://{self.config.hostname}/machine/file/gcodes/{gcode_name}'

        self.logger.debug(f"sending {filename} to {upload_uri}")

        request = QtNetwork.QNetworkRequest(QtCore.QUrl(upload_uri))
        self.__reply = self._manager.put(request, file.readAll())
        self.__reply.uploadProgress.connect(lambda a, b: self.__upload_progress(gcode_name, a, b))
        self.__reply.finished.connect(lambda: self.__upload_done(gcode_name))
        self.__reply.error.connect(lambda a: self.__upload_error(gcode_name, a))
        self._is_uploading = True

    def __upload_progress(self, filename, bytes_sent, bytes_total):
        if bytes_total:  # When upload is done __upload_progress(0, 0) is called => avoid division per zero
            progress = int(float(bytes_sent) * 100 / bytes_total)
            self.ui.statusbar.showMessage(f"({progress}%) Uploading {filename} ...")

    def __upload_done(self, filename):
        self._is_uploading = False

        error = self.__reply.error()
        if error == QtNetwork.QNetworkReply.NetworkError.NoError:
            msg = f"{filename} uploaded successfully"
            self.logger.debug(msg)
            self.ui.statusbar.showMessage(msg)
            if self.config.print_after_upload:
                self.__start_print(filename)

    def __upload_error(self, filename, err):
        self._is_uploading = False
        self.logger.error(f"Failed to upload {filename}: {err}")
        self.ui.statusbar.showMessage(f"Failed to upload {filename}")

    def __start_print(self, filename):
        cmd = f'M32 "0:/gcodes/{filename}"'
        self.__reply = self.__send_command(cmd)
        self.__reply.finished.connect(lambda: self.__print_started(filename))
        self.__reply.error.connect(lambda a: self.__print_error(filename, a))

    def __send_command(self, cmd):
        send_cmd_uri = f'http://{self.config.hostname}/machine/code'
        self.logger.debug(f"sending {cmd} to {send_cmd_uri}")

        request = QtNetwork.QNetworkRequest(QtCore.QUrl(send_cmd_uri))
        data = QtCore.QByteArray(bytes(cmd, 'utf8'))
        return self._manager.post(request, data)

    def __print_started(self, filename):
        error = self.__reply.error()
        if error == QtNetwork.QNetworkReply.NetworkError.NoError:
            self.logger.debug(f"Print started: {filename}")
            self.ui.statusbar.showMessage(f"Print started: {filename}")

            if self.__del_localfile_after_upload:
                # TODO: delete local file
                pass

    def __print_error(self, filename, err):
        self.logger.error(f"Failed to print {filename}: {err}")
        self.ui.statusbar.showMessage(f"Failed to print {filename}")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = DWC_Gcode_uploader()
    sys.exit(app.exec_())
