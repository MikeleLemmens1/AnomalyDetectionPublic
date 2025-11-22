"""
This module is used for initializing the loggers and includes the following functions: 
    * create_logger: creates a logger with a set logging file and level
    * get_info_logger: creates an info logger and returns this
    * get_error_logger: creates an error logger and returns this
"""

import logging
import os

def create_logger(name, log_file, level=logging.INFO):
    """
    This function creates a logger with a set logging file and level

    Args:
        name (String): name of the logger
        log_file (String): path to where the logging file will be
        level (_Level, optional): the logging level. Needs to be part of the logging module. Defaults to logging.INFO.

    Returns:
        Logger: the new logger that was just created
    """
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)

    return logger

def get_info_logger():
    """
    This function creates an info logger and returns this

    Returns:
        Logger: the info logger
    """
    path_to_info = os.path.abspath('logger/info_logs.log')
    info_logger = create_logger("info_logging", path_to_info)
    info_logger.addHandler(logging.StreamHandler())

    return info_logger


def get_error_logger():
    """
    This function creates and error logger and returns this

    Returns:
        Logger: the error logger
    """
    path_to_error = os.path.abspath('logger/error_logs.log')
    error_logger = create_logger("error_logging", path_to_error, logging.ERROR)
    error_logger.addHandler(logging.StreamHandler())
    
    return error_logger
