import logging
import time

from jobs.cron_print import print_message




logger = logging.getLogger(__name__)

def hello_job():
    logger.info("hello_job Start")
    time.sleep(2)
    print_message("hello_job_test")
    logger.info("hello_job End")

def cron_job():
    logger.info("cron_job Start")
    time.sleep(1)
    logger.info("cron_job End")
