import logging.config


def get_dict_config(name: str, level: str = "DEBUG"):
    dict_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "formatter": {
                "format": "%(levelname)s | %(asctime)s | %(name)s | %(funcName)s | %(lineno)d | %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "formatter",
            },
        },
        "loggers": {
            name: {
                "level": level,
                "handlers": ["console"],
            }
        },
    }
    return dict_config


def get_logger(logger_name: str, level: str = "DEBUG") -> logging.Logger:
    logging.config.dictConfig(get_dict_config(name=logger_name, level=level))
    logger = logging.getLogger(logger_name)
    return logger
