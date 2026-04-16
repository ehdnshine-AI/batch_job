import logging
import os
import time
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

import yaml
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import job_funcs as jobs


def setup_logger():
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    timed_handler = TimedRotatingFileHandler(
        "logs/app_daily.log",
        when="midnight",
        interval=1,
        backupCount=7,
    )

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    timed_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(timed_handler)


def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_job_function(func_name):
    if not hasattr(jobs, func_name):
        raise ValueError(f"{func_name} 함수가 job_funcs.py에 없음")
    return getattr(jobs, func_name)


def execute_job(func_name, job_name):
    logger = logging.getLogger(job_name)
    func = get_job_function(func_name)

    try:
        logger.info(f"[START] {job_name}")
        func()
        logger.info(f"[END] {job_name}")
    except Exception as e:
        logger.exception(f"[ERROR] {job_name} 실행 실패: {e}")


def register_jobs(scheduler, config):
    for job in config.get("jobs", []):
        job_name = job["job_name"]
        schedule_type = job["schedule_type"]
        func_name = job["func"]

        get_job_function(func_name)

        if schedule_type == "interval":
            scheduler.add_job(
                execute_job,
                "interval",
                seconds=job["seconds"],
                args=[func_name, job_name],
                id=job_name,
                replace_existing=True,
            )
        elif schedule_type == "cron":
            minute, hour, day, month, day_of_week = job["cron"].split()
            trigger = CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
            )
            scheduler.add_job(
                execute_job,
                trigger=trigger,
                args=[func_name, job_name],
                id=job_name,
                replace_existing=True,
            )
        else:
            raise ValueError(f"지원하지 않는 스케줄 타입: {schedule_type}")

        logging.info(f"Job 등록 완료: {job_name}")


def main():
    setup_logger()
    config = load_config()

    os.makedirs("db", exist_ok=True)

    jobstores = {
        "default": SQLAlchemyJobStore(url="sqlite:///db/scheduler.db")
    }
    scheduler = BackgroundScheduler(jobstores=jobstores)

    register_jobs(scheduler, config)
    scheduler.start()

    logging.info("Scheduler 시작")

    try:
        while True:
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logging.info("Scheduler 종료")


if __name__ == "__main__":
    main()
