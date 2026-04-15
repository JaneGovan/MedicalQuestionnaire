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


def set_logger_v1():
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


class _DailyFileHandler(logging.FileHandler):
    """每天一个日志文件，首次写入时按需创建，自动清理 30 天前的文件。"""

    def __init__(self, log_dir, encoding='utf-8'):
        self._log_dir = log_dir
        self._current_date = None
        # 先不打开任何文件，等第一条日志进来再创建
        super().__init__(self._path_for(datetime.now()), mode='a', encoding=encoding, delay=True)

    def _path_for(self, dt):
        date_str = dt.strftime('%Y-%m-%d')
        return os.path.join(self._log_dir, f'info.log.{date_str}')

    def _cleanup_old(self):
        """删除 30 天前的日志文件"""
        cutoff = (datetime.now() - __import__('datetime').timedelta(days=30)).strftime('%Y-%m-%d')
        if not os.path.isdir(self._log_dir):
            return
        for fname in os.listdir(self._log_dir):
            if fname.startswith('info.log.') and fname[-10:] < cutoff:
                try:
                    os.remove(os.path.join(self._log_dir, fname))
                except OSError:
                    pass

    def emit(self, record):
        today = datetime.now().strftime('%Y-%m-%d')
        if today != self._current_date:
            self._current_date = today
            new_path = self._path_for(datetime.now())
            if self.stream is not None:
                self.close()
            self.baseFilename = new_path
            os.makedirs(self._log_dir, exist_ok=True)
            self._cleanup_old()
        super().emit(record)


def set_logger_v2():
    log_dir = Config["log_file"]
    logger = logging.getLogger(Config["project_name"])
    fmt = logging.Formatter(
        "%(asctime)s | {project_name} | user_id=%(user_id)s | request_id=%(request_id)s | [%(levelname)s] | [%(filename)s- %(lineno)d] | %(message)s".format(project_name=Config["project_name"])
    )
    handler = _DailyFileHandler(log_dir, encoding='utf-8')
    handler.setFormatter(fmt)
    handler.setLevel(logging.INFO)
    handler.addFilter(UserAndRequestIDFilter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

Logger = set_logger_v2()