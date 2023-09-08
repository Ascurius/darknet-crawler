import logging
import os
import config

class Helper:
    def __init__(self, path):
        self.init_logger(path)

    def init_logger(self, path):
        log_path = os.path.expanduser(path)
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        log = logging.getLogger("darknet-crawler")
        log.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(
            logging.DEBUG if config.LOGGING_VERBOSITY > 1 else
            logging.INFO if config.LOGGING_VERBOSITY == 1 else
            logging.WARNING
        )
        file_formatter = logging.Formatter(
            "%(asctime)s %(name)-8s %(levelname)-7s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_formatter = logging.Formatter("%(levelname)-5s %(message)s")
        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(file_formatter)
        log.addHandler(console_handler)
        log.addHandler(file_handler)
        self.log = log

    