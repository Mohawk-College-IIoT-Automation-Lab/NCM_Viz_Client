#!/usr/bin/env python3

import logging
import time

def initialize_logging(log_name: str, log_level=logging.DEBUG, status_bar=None):
    log_file = f"{log_name}.log"
    logger = logging.getLogger()
    logger.name = log_name

    fmtter = logging.Formatter('[%(asctime)s]-[%(levelname)s]: %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(fmtter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(fmtter)
    logger.addHandler(file_handler)

    time.sleep(1)  # one second to setup

    logger.setLevel(log_level)

initialize_logging("Test")
logging.info("Hello")
logging.warning("Hello warn")
