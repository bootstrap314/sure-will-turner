import logging
import json
import sys

logger = logging.getLogger(__name__)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        # convert the log record to a dictionary
        log_dict = {
            "timestamp": record.created,
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # convert the dictionary to JSON format
        log_json = json.dumps(log_dict)

        # return the JSON-formatted log message
        return log_json


def configureLogging(log_level, log_destination, log_format):
    if log_destination == "stdout":
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.FileHandler(log_destination)

    if log_format == "json":
        handler.setFormatter(JsonFormatter())

    if log_level == "DEBUG":
        level = logging.DEBUG
    elif log_level == "ERROR":
        level = logging.ERROR
    elif log_level == "INFO":
        level = logging.INFO
    elif log_level == "WARN":
        level = logging.WARN

    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(message)s",
        level=level,
        handlers=[handler],
    )
