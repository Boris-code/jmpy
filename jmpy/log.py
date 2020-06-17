# -*- coding: utf-8 -*-
"""
Created on 2020/6/17 12:17 下午
---------
@summary:
---------
@author: Boris
"""
import logging
import sys

# set up logging
logger = logging.getLogger("encrypt-py")

format_string = (
    "%(asctime)s|%(filename)s|%(funcName)s|line:%(lineno)d|%(levelname)s| %(message)s"
)
formatter = logging.Formatter(format_string, datefmt="%Y-%m-%dT%H:%M:%S")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.stream = sys.stdout

logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
