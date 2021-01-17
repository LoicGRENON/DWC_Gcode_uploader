# -*- coding: utf-8 -*-

import logging


class Config:

    def __init__(self):
        self.watched_path = ""
        self.hostname = ""
        self.logging_level = logging.DEBUG
        self.delete_after_upload = False
        self.print_after_upload = False

        self.read()

    def read(self):
        # TODO: read from a proper config file
        self.watched_path = "E:\Impression3D\Gcodes"
        self.hostname = "192.168.1.69"
        self.delete_after_upload = True
        self.print_after_upload = True

    def save(self):
        # TODO: Save current config
        pass
