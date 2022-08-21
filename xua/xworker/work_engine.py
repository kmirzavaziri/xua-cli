import logging, logging.handlers
import signal
import json
from concurrent.futures import ThreadPoolExecutor

import requests
import time
from xua import helpers

from . import datatypes


class WorkEngineGracefulExitException(Exception):
    pass


class WorkEngine:
    __config: datatypes.WorkerConfig = None
    __loop: bool = None
    __loggers: dict = None
    __pool: ThreadPoolExecutor = None

    @classmethod
    def start(cls, config_path):
        cls.__initiate(config_path)
        cls.__start_loop()

    @classmethod
    def __initiate(cls, config_path):
        cls.__config = datatypes.WorkerConfig(config_path)
        cls.__loop = cls.__initiate_loop()
        cls.__loggers = cls.__initiate_loggers()
        cls.__pool = ThreadPoolExecutor(5)  # @TODO read from config

    @staticmethod
    def __initiate_loop():
        def handler(signum, frame):
            raise WorkEngineGracefulExitException
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
        return True

    @classmethod
    def exit_gracefully(cls):
        try:
            cls.__loop = False
            cls.__pool.shutdown(wait=True, cancel_futures=True)
            helpers.Logger.log(helpers.Logger.SUCCESS, '', 'Exited gracefully.')
        except WorkEngineGracefulExitException:
            cls.__pool.shutdown(wait=False, cancel_futures=True)
            helpers.Logger.log(helpers.Logger.SUCCESS, '', 'Exited forcefully.')
        finally:
            exit()

    @classmethod
    def __initiate_loggers(cls):
        loggers = {}
        for server_name in cls.__config.servers:
            server = cls.__config.servers[server_name]
            server.logs.path.parent.mkdir(parents=True, exist_ok=True)
            loggers[server_name] = logging.getLogger(f'xworker:{server_name}')
            loggers[server_name].setLevel(logging.INFO)
            loggers[server_name].addHandler(logging.handlers.TimedRotatingFileHandler(
                server.logs.path,
                when=server.logs.rotating.period.unit.abbr,
                interval=server.logs.rotating.period.number,
                backupCount=server.logs.rotating.backup_count,
            ))
            loggers[server_name].info('XWorker engine started.')

        return loggers

    @classmethod
    def __start_loop(cls):
        try:
            while cls.__loop:
                now = datatypes.Time.now()
                for job in cls.__config.jobs:
                    if cls.__should_run_job(job, now):
                        for server_name in job.run_on:
                            cls.__run_job(job, now, server_name)
                if not cls.__loop:
                    break
                time.sleep(1)
        except WorkEngineGracefulExitException:
            cls.exit_gracefully()

    @staticmethod
    def __should_run_job(job: datatypes.Job, now: datatypes.Time) -> bool:
        number = job.period.number
        unit = job.period.unit
        occurrences = job.period.occurrences
        condition = now.get_unit_value(unit) % number == 0
        condition = condition and any([
            occurrence.time.equal_from_unit_to_end(now, unit=unit)
            for occurrence in occurrences
        ])
        # @TODO check for overlap
        # @TODO we don't need to be exactly on time, if we pass it by even 1 sec, this method ignores the task,
        #       we should find a way to avoid this issue.
        return condition

    @classmethod
    def __run_job(cls, job: datatypes.Job, now: datatypes.Time, server_name: str) -> None:
        def __run_job():
            method = requests.get if job.method == datatypes.HttpMethod.GET else requests.post
            url = cls.__config.servers[server_name].base_url + '/' + job.resource
            request = json.dumps(job.request)
            headers = cls.__config.servers[server_name].headers
            http_response = method(url=url, data={'request': request}, headers=headers)
            if job.store_logs:
                try:
                    response = json.dumps(http_response.json(), ensure_ascii=False, indent=4)
                except json.JSONDecodeError:
                    response = str(http_response.content)
                response = ('\n' + response).replace('\n', '\n' + ' ' * 4)
                cls.__loggers[server_name].info(f'{now}: {job.method} {job.resource} {request}{response}\n')

        def __run_job_wrapper():
            try:
                __run_job()
            except WorkEngineGracefulExitException:
                cls.exit_gracefully()
        cls.__pool.submit(__run_job_wrapper)
