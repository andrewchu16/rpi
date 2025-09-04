# Setup logging at module level
import atexit
import json
import logging
from logging.handlers import QueueHandler


def setup_logging():
    with open("./logging_config.json", "r") as f:
        logging.config.dictConfig(json.load(f))
    queue_handler: QueueHandler = logging.getHandlerByName("queue_handler")

    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)
logger.info("Logging initialized")