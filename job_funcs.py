import logging
import time

from jobs.cron_print import print_message




logger = logging.getLogger(__name__)

def hello_job():
    logger.info("hello_job 시작")
    time.sleep(2)
    print_message("hello_job_test")
    logger.info("hello_job 종료")

def cron_job():
    logger.info("cron_job 실행")
    time.sleep(1)
    logger.info("cron_job 완료")
