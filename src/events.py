# -*- coding: utf-8 -*-

import logging
import requests
import time
from pathlib import Path
from plyer import notification
from watchdog.events import RegexMatchingEventHandler


class FileEventHandler(RegexMatchingEventHandler):
    GCODE_REGEX = [r".*\.gcode$"]

    def __init__(self, cli_args):
        super().__init__(self.GCODE_REGEX)
        self.__cli_args = cli_args
        self.__prev_file = None
        self.__last_event_time = time.time()

        logging.basicConfig(level=logging.DEBUG)
        self.__logger = logging.getLogger(self.__class__.__name__)

    def on_created(self, event):
        # For some reasons, the file seems to be created 3 times when exporting from ideaMaker
        # So we filter it out here to ensure to upload the file only one time.
        if event.src_path == self.__prev_file and int(time.time() - self.__last_event_time) < 1:
            return False
        self.__logger.debug(f"{event.src_path} has been created!")
        time.sleep(1)  # Needed to let the time to the external handle to close the file
        self.upload_to_dwc(event.src_path)
        self.__prev_file = event.src_path
        self.__last_event_time = time.time()

    def upload_to_dwc(self, filepath):
        self.__logger.debug(f"Uploading {filepath} ...")
        p = Path(filepath)
        fname = self._sanitize_filename(p.name)
        err_code = 0
        try:
            with open(filepath, 'rb') as data:
                self.__notify(
                    title=f"Uploading {fname}",
                    message=f"{fname} is uploading to DWC"
                )
                r = requests.put(f'http://192.168.1.38/machine/file/gcodes/{fname}', data=data)
                self.__logger.debug(f"Uploading status code: {r.status_code} ...")
                err_code = 0 if r.status_code == 201 else 1
        except OSError as e:
            self.__logger.error(e)
            self.__notify(
                title=f"Upload error",
                message=f"Error when uploading {fname} to DWC: {e}"
            )

        if not err_code and not self.__cli_args.upload_only:
            self.start_printing(p.name)

        self.__delete_local_gcode_file(p)

    def start_printing(self, filename):
        self.__logger.debug(f"Start printing '{filename}' ...")
        self.__notify(
            title=f"Printing {filename}",
            message=f"{filename} is now printing"
        )
        r = requests.post('http://192.168.1.38/machine/code', data=f'M32 "0:/gcodes/{filename}"')
        self.__logger.debug(f"DoCode status code: {r.status_code} ...")

    def _sanitize_filename(self, filename):
        # Quoting the filename two times helps to keep the same filename at DWC side in case of special chars
        # but DWC might not recognize it properly, probably due to some url encoding issue
        # See https://github.com/Duet3D/DuetWebControl/issues/320
        # fname_sanitized = requests.utils.quote(requests.utils.quote(filename))
        fname_sanitized = requests.utils.quote(filename)
        return fname_sanitized

    def __notify(self, title, message, timeout=10):
        if self.__cli_args.silent:
            return

        notification.notify(
            title=title,
            message=message,
            app_name="DWC_Gcode_uploader",
            timeout=timeout
        )

    def __delete_local_gcode_file(self, file_path):
        self.__logger.debug("Cleaning local files")
        try:
            file_path.unlink()
            # ideamaker also saves a .data file
            file_path.with_suffix('.data').unlink()
        except FileNotFoundError:
            pass
        except OSError as e:
            self.__logger.error(e)
            self.__notify(
                title=f"Cleaning error",
                message=f"Error when cleaning directory: {e}"
            )
