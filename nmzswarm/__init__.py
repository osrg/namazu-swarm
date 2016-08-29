"""Namazu Swarm
"""
import logging
import os
import sys


def init_logger(debug: bool) -> logging.Logger:
    """initializes and return the logger
    """
    logger = logging.getLogger(__name__)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s' +
        ' (at %(filename)s:%(lineno)d)')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

LOG = init_logger(os.getenv('NMZSWARM_DEBUG') is not None)
