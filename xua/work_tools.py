from genericpath import exists
import json
import os
import requests
import time
import datetime
import jdatetime

from xua.constants import WORKER_CONFIG
from xua.exceptions import UserError


class WorkEngine:
    def __init__(self, config):
        self.config = config

    def start(self):
        while True:
            now = self.now()
            for job in self.config.config[WORKER_CONFIG.KEY.JOBS]:
                if self.shouldRunJob(job, now):
                    self.runJob(job, now)
            time.sleep(1)

    @staticmethod
    def shouldRunJob(job, now):
        every = job[WORKER_CONFIG.KEY.JOBS_EVERY]
        number = every[WORKER_CONFIG.KEY.JOBS_EVERY_NUMBER]
        unit = every[WORKER_CONFIG.KEY.JOBS_EVERY_UNIT]

        return now[unit] % number == 0 and any([all([at[atPartUnit] == now[atPartUnit] for atPartUnit in at]) for at in every[WORKER_CONFIG.KEY.JOBS_EVERY_AT]])

    def runJob(self, job, now):
        method = requests.get if job[WORKER_CONFIG.KEY.JOBS_METHOD] == WORKER_CONFIG.VALUE.JOBS_METHOD.GET else requests.post
        url = self.config.cliArgs.base_url + '/' + \
            job[WORKER_CONFIG.KEY.JOBS_RESOURCE]
        request = json.dumps(job[WORKER_CONFIG.KEY.JOBS_REQUEST])
        headers = {}
        for header in self.config.cliArgs.header:
            keyValue = header.split(':', 1)
            if len(keyValue) != 2:
                raise UserError(f"Header '{header}' must contain a colon.")
            key, value = keyValue
            headers[key] = value.lstrip()
        r = method(url=url, data={'request': request}, headers=headers)

        if job[WORKER_CONFIG.KEY.JOBS_STORE_LOGS]:
            try:
                response = json.dumps(r.json(), ensure_ascii=False, indent=4)
            except:
                response = str(r.content)
            response = ('\n' + response).replace('\n', '\n' + ' ' * 4)

            logsFile = os.path.join(os.path.dirname(self.config.cliArgs.config), self.config.config[WORKER_CONFIG.KEY.LOGS][WORKER_CONFIG.KEY.LOGS_DIR], now['_'].strftime(
                '%Y-%m-%d'), job[WORKER_CONFIG.KEY.JOBS_RESOURCE] + '.log')
            logsDir = os.path.dirname(logsFile)
            os.makedirs(logsDir, 0o777, exist_ok=True)
            with open(logsFile, 'a+') as f:
                f.write(
                    f"{now['_'].strftime('%H:%M:%S')}: {job[WORKER_CONFIG.KEY.JOBS_METHOD]} {job[WORKER_CONFIG.KEY.JOBS_RESOURCE]} {request}{response}\n")
        return

    def now(self):
        if self.config.config[WORKER_CONFIG.KEY.CALENDAR] == WORKER_CONFIG.VALUE.CALENDAR.GREGORIAN:
            now = datetime.datetime.now()
        elif self.config.config[WORKER_CONFIG.KEY.CALENDAR] == WORKER_CONFIG.VALUE.CALENDAR.JALALI:
            now = jdatetime.datetime.now()
        else:
            raise Exception(
                f"Unknown calendar {self.config.config[WORKER_CONFIG.KEY.CALENDAR]}")

        return {
            '_': now,
            WORKER_CONFIG.VALUE.JOBS_EVERY_UNIT.SECOND: now.second,
            WORKER_CONFIG.VALUE.JOBS_EVERY_UNIT.MINUTE: now.minute,
            WORKER_CONFIG.VALUE.JOBS_EVERY_UNIT.HOUR: now.hour,
            WORKER_CONFIG.VALUE.JOBS_EVERY_UNIT.DAY: now.day,
            WORKER_CONFIG.VALUE.JOBS_EVERY_UNIT.MONTH: now.month,
            WORKER_CONFIG.VALUE.JOBS_EVERY_UNIT.YEAR: now.year,
        }
