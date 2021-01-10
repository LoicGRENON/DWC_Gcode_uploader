# -*- coding: utf-8 -*-

import argparse
import time
from watchdog.observers import Observer

from events import FileEventHandler


class GcodeUploader:

    def __init__(self, cli_args):
        self.__src_path = cli_args.path
        self.__event_handler = FileEventHandler(cli_args)
        self.__event_observer = Observer()

    def run(self):
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def start(self):
        self.__schedule()
        self.__event_observer.start()

    def stop(self):
        self.__event_observer.stop()
        self.__event_observer.join()

    def __schedule(self):
        self.__event_observer.schedule(
            self.__event_handler,
            self.__src_path,
            recursive=False
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        help="Local directory to monitor for new G-Code files",
        type=str)
    parser.add_argument(
        "-u", "--upload-only",
        help="Only upload the file to DWC. Do not print them automatically",
        action="store_true")
    parser.add_argument(
        "-k", "--keep",
        help="Keep the file on the local directory after upload",
        action="store_true")
    parser.add_argument(
        "-s", "--silent",
        help="Silent mode. Do not display desktop notifications",
        action="store_true")
    cli_args = parser.parse_args()

    # Run forever
    GcodeUploader(cli_args).run()
