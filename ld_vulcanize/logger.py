# -*- encoding: utf-8 -*-
"""
Customized Python logger
"""

import logging


def make_logger(name, doctest_mode=False):
    logger = logging.getLogger(name)
    if len(logger.handlers) == 0:
        if doctest_mode:
            formatter = logging.Formatter('[%(name)s] %(levelname)s: %(message)s')
        else:
            formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s',
                                          datefmt='%H:%M:%S')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    return logger


def enable_doctest_mode():
    global log
    log = make_logger('ld-vulcanize', True)    


log = make_logger('ld-vulcanize')    

