import logging
import sys
import time

class KeyValueFormatter(logging.Formatter):
    def format(self, record):
        base = f"\n[{record.funcName}] time={int(time.time())} level={record.levelname} msg=\"{record.getMessage()}\""
        if hasattr(record, "extra_data"):
            extras = " ".join(f"{k}={v!r}" for k, v in record.extra_data.items())
            return f"{base} {extras}"
        return base


def setup_logger():
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(KeyValueFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = setup_logger()
