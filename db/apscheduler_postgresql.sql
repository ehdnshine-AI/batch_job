-- 1. 사용자 생성
CREATE USER scheduler_user WITH PASSWORD 'scheduler_user123';

-- 2. 데이터베이스 생성 (소유자를 사용자로 지정)
CREATE DATABASE scheduler_db
    WITH OWNER = scheduler_user
    ENCODING = 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TEMPLATE = template0;

-- 3. 데이터베이스 접속 권한 부여
GRANT ALL PRIVILEGES ON DATABASE scheduler_db TO scheduler_user;


CREATE TABLE IF NOT EXISTS public.apscheduler_jobs (
    id VARCHAR(191) PRIMARY KEY,
    next_run_time DOUBLE PRECISION,
    job_state BYTEA NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_apscheduler_jobs_next_run_time
    ON public.apscheduler_jobs (next_run_time);
