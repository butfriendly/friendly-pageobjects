import logging

logger = logging.getLogger()
logger.addHandler(logging.FileHandler('test.log'))
logger.setLevel(logging.DEBUG)
