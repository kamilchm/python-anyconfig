#
# Copyright (C) 2013, 2014 Satoru SATOH <ssato @ redhat.com>
# License: MIT
#
"""anyconfig globals.
"""
import logging
import os


AUTHOR = 'Satoru SATOH <ssat@redhat.com>'
VERSION = "0.0.5"

_LOGGING_FORMAT = "%(asctime)s %(name)s: [%(levelname)s] %(message)s"


def get_logger(name="anyconfig", log_format=_LOGGING_FORMAT,
               level=logging.WARNING):
    """
    Initialize custom logger.
    """
    if os.environ.get("ANYCONFIG_DEBUG", False):
        level = logging.DEBUG

    logging.basicConfig(level=level, format=log_format)
    logger = logging.getLogger(name)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(handler)

    return logger


LOGGER = get_logger()

# vim:sw=4:ts=4:et:
