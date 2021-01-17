# -*- coding: utf-8 -*-

from PySide2 import QtCore
from watchdog.events import RegexMatchingEventHandler
from watchdog.observers import Observer


class GCodeFileEventHandler(RegexMatchingEventHandler, QtCore.QObject):
    GCODE_REGEX = [r'.*\.(?:gcode|g)$']
    created_file_sig = QtCore.Signal(str)

    def __init__(self):
        super().__init__(self.GCODE_REGEX)

        self.__prev_file = None
        self.__event_timer = QtCore.QTime()

    def on_created(self, event):
        # For some reasons, the file seems to be created 3 times when exporting from ideaMaker
        # So we filter it out here to ensure to upload the file only one time.
        if event.src_path == self.__prev_file and self.__event_timer.elapsed() < 1000:
            return False

        self.created_file_sig.emit(event.src_path)
        self.__prev_file = event.src_path
        self.__event_timer.restart()


class FilePathWatcher(QtCore.QThread):
    def __init__(self, path=None):
        super().__init__()
        self.path = path
        self.observer = Observer()
        self.event_handler = GCodeFileEventHandler()
        self.change_path(path)

    def run(self):
        pass

    def get_emitter(self):
        return self.event_handler

    def change_path(self, path):
        if not path:
            return

        self.observer.unschedule_all()
        self.observer.schedule(self.event_handler, path, recursive=False)
        self.path = path

        if not self.observer.is_alive():
            self.observer.start()
