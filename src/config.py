import os
import sys
import logging.config
from pycomm3.logger import configure_default_logger
from environs import Env

env = Env()
env.read_env()

if getattr(sys, "frozen", False):
    # If the application is run as a bundled executable.
    application_path = sys._MEIPASS
    logs_path = os.path.dirname(sys.executable)
else:
    # If it's run as a regular script.
    application_path = os.path.dirname(os.path.abspath(__file__))
    logs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

env_path = os.path.join(application_path, ".env")
env.read_env(env_path)

ROUTES = {"GC": {1: "24", 2: "48", 3: "72"}}
MAX_RETRIES = env.int("MAX_RETRIES")
RETRY_DELAY = env.int("RETRY_DELAY")
PLC_3L3 = env.str("PLC_3L3")
PLC_3L6 = env.str("PLC_3L6")
SFCS_SERVER = env.str("SFCS_SERVER")
STAGE = env.str("STAGE")
CATEGORY = env.str("CATEGORY")
PLC_DELAY = env.float("PLC_DELAY")
MAX_BYTES = env.int("MAX_BYTES")
BACKUP_COUNT = env.int("BACKUP_COUNT")

# Create logs directory if it doesn't exist.

LOGS_DIR = os.path.join(logs_path, "logs")
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Logging configuration.

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "filename": "logs/plc_auto_scanning.log",
            "maxBytes": MAX_BYTES,
            "backupCount": BACKUP_COUNT,
            "encoding": "utf8",
        },
    },
    "root": {"level": "INFO", "handlers": ["console", "file"]},
}

logging.config.dictConfig(LOGGING_CONFIG)

# Create a logger for the application.
logger = logging.getLogger("App")

# Configure the default logger for pycomm3.
configure_default_logger(level=logging.WARNING, filename="logs/pycomm3.log")
