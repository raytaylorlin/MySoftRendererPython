#!/usr/bin/env python3

import logging
import sys

LOG_FILENAME = 'log.log'


def setup_custom_logger(name):
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    fileHandler = logging.FileHandler(LOG_FILENAME, mode='w')
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(logging.DEBUG)

    streamHandler = logging.StreamHandler(sys.stdout)
    streamHandler.setFormatter(formatter)
    streamHandler.setLevel(logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fileHandler)
    # 启用以下这句以输出到控制台
    logger.addHandler(streamHandler)
    return logger


logger = setup_custom_logger('root')

# 启用下面这句以禁用日志
# logging.disable(logging.CRITICAL)
