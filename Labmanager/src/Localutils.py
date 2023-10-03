import logging
from datetime import datetime


def log_event(str,printout=False):
    logging.info(datetime.now().strftime("%d.%b %Y %H:%M:%S - ")+str)