import logging
import os
import pymongo

class Helper:
    def __init__(self, logging_verbose, database_host):
        self.init_logger(logging_verbose)
        self.init_database(database_host)

    def init_logger(self, verbose):
        log_path = os.path.expanduser("~/darknet-crawler/forums.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        log = logging.getLogger("darknet-crawler")
        log.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(
            logging.DEBUG if verbose > 1 else
            logging.INFO if verbose == 1 else
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

    def init_database(self, db_host):
        self.client = pymongo.MongoClient(db_host)
        self.database = self.client["praktikum"]
        self.collection_forums = self.database["forums"]
        self.collection_users = self.database["users"]

    def clear_collection(self, collection):
        if hasattr(self, "collection_{}".format(collection)):
            collection_attr = getattr(self, "collection_{}".format(collection))
            response = collection_attr.delete_many({})
            self.log.debug("Successfully deleted {} documents".format(response.deleted_count))
        else:
            self.log.error("Could not find the specified collection")