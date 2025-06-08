
import os
from logging.config import dictConfig

def setup_logging(
    name: str = "scytale_pr_report",
    log_dir: str = "logs",
    filename: str = "scytale-pr-report.log",
    level: str = "INFO",
    max_bytes: int = 5*1024*1024,
    backup_count: int = 3
):

    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, filename)

    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s %(name)s %(levelname)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": level,
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                "level": level,
                "filename": log_path,
                "maxBytes": max_bytes,
                "backupCount": backup_count
            }
        },
        "root": {
            "handlers": ["console", "file"],
            "level": level
        }
    })
