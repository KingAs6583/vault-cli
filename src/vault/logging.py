# vault/logging.py

import logging


def setup_logger(name: str = "vault", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("[%(levelname)s] %(message)s")
        handler.setFormatter(formatter)

        # Filter to redact evident secrets in log messages
        class RedactFilter(logging.Filter):
            def filter(self, record):
                try:
                    if isinstance(record.msg, str):
                        record.msg = record.msg.replace("password=", "password=****")
                        record.msg = record.msg.replace("secret=", "secret=****")
                    return True
                except Exception:
                    return True

        handler.addFilter(RedactFilter())
        logger.addHandler(handler)

    return logger
