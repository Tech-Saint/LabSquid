import logging
from datetime import datetime

logging.basicConfig(filename='Debug.txt', level=logging.INFO)

def log_event(str,printout=False):
    logging.info(datetime.now().strftime("%d.%b %Y %H:%M:%S - ")+str)