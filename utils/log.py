import logging
import sys
import os
import time
from contextvars import ContextVar
import yaml
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
sys.path.append(".")

USER_ID = ContextVar("user_id", default="NO_USER_ID")
REQUEST_ID = ContextVar("request_id", default="NO_REQUEST_ID")


class UserAndRequestIDFilter(logging.Filter):
    def filter(self, record):
        record.user_id = USER_ID.get()
        record.request_id = REQUEST_ID.get()
        return True


def get_config(yaml_file: str = "config.yaml"):
    def join_constructor(loader, node):
        seq = loader.construct_sequence(node)
        return os.path.join(*map(str, seq))
    yaml.SafeLoader.add_constructor('!join', join_constructor)

    with open(yaml_file, "r", encoding="utf-8") as yf:
        config = yaml.safe_load(yf)
    return config


Config = get_config()


def set_logger():
    datetime_str = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")
    dir_name = os.path.join(Config["log_file"], datetime_str)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    full_path = os.path.join(dir_name, "info.log")
    logger = logging.getLogger(Config["project_name"])
    fmt = logging.Formatter("%(asctime)s | {project_name} | user_id=%(user_id)s | request_id=%(request_id)s | [%(levelname)s] | [%(filename)s- %(lineno)d] | %(message)s".format(project_name=Config["project_name"]))
    handler = RotatingFileHandler(
        filename=full_path,
        mode="a",
        maxBytes=20*1024*1024,
        backupCount=5,
        encoding="utf-8"
    )
    handler.setFormatter(fmt)
    handler.setLevel(logging.INFO)
    handler.addFilter(UserAndRequestIDFilter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


Logger = set_logger()

