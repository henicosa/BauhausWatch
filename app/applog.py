import logging
import os

# Create log directory if it doesn't exist
log_dir = "log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename="log/application.log",
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S'
)


def error(message):
    print(message)
    logging.error(message)


def info(message):
    print(message)
    logging.info(message)


def debug(message):
    print(message)
    logging.debug(message)


def warning(message):
    print(message)
    logging.warning(message)