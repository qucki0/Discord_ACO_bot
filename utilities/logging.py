import logging
import logging.handlers
import os.path

imported_loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
for imported_logger in imported_loggers:
    imported_logger.setLevel(logging.WARNING)
log_format = "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)s]  %(message)s"
log_formatter = logging.Formatter(log_format)
sh = logging.StreamHandler()
sh.setFormatter(log_formatter)
sh.setLevel(logging.INFO)
if not os.path.exists("./logs"):
    os.mkdir("logs")
if not os.path.exists("./logs/info"):
    os.mkdir("logs/info")
if not os.path.exists("./logs/debug"):
    os.mkdir("logs/debug")
fh_info = logging.handlers.RotatingFileHandler(filename="logs/info/logs.log", maxBytes=1024 * 1024 * 5, backupCount=5,
                                               encoding="urf-8")
fh_info.setFormatter(log_formatter)
fh_info.setLevel(logging.INFO)
fh_debug = logging.handlers.RotatingFileHandler(filename="logs/debug/logs.log", maxBytes=1024 * 1024 * 5, backupCount=5,
                                                encoding="urf-8")
fh_debug.setFormatter(log_formatter)
fh_debug.setLevel(logging.DEBUG)
handlers = [sh, fh_info, fh_debug]


class ContextFilter(logging.Filter):
    def filter(self, record):
        if "private_key" in str(record):
            return False
        return True


def get_logger(name=None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logging.getLogger().hasHandlers():
        return logger
    logger.setLevel(logging.DEBUG)
    logger.addFilter(ContextFilter())
    for handler in handlers:
        logger.addHandler(handler)
    logger.debug(f"logger {name} setup successful")
    return logger
