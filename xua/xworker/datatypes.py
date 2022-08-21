# @TODO check for extra unwanted json keys everywhere

import json
import os
import datetime
from enum import Enum
from pathlib import Path

import jdatetime

from xua.exceptions import UserError


class XuaEnum(Enum):
    @classmethod
    def str(cls):
        return '(' + ', '.join(map(str, cls.__members__.values())) + ')'

    def __str__(self):
        return str(self.value)

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class Calendar(XuaEnum):
    JALALI = 'jalali'
    GREGORIAN = 'gregorian'


class TimeUnit(XuaEnum):
    SECOND = 'second'
    MINUTE = 'minute'
    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    QUARTER = 'quarter'
    YEAR = 'year'

    def has_below(self):
        return self != self.SECOND

    def below(self):
        return {
            self.MINUTE: self.SECOND,
            self.HOUR: self.MINUTE,
            self.DAY: self.HOUR,
            self.WEEK: self.DAY,
            self.MONTH: self.DAY,
            self.QUARTER: self.MONTH,
            self.YEAR: self.MONTH,
        }[self]

    def limit_calculators(self):
        return {
            self.MINUTE: lambda number, calendar: [0, 60 * number - 1],
            self.HOUR: lambda number, calendar: [0, 60 * number - 1],
            self.DAY: lambda number, calendar: [0, 24 * number - 1],
            self.WEEK: lambda number, calendar: [1, 7 * number],
            self.MONTH: lambda number, calendar: [1, 29 * number] if calendar == 'jalali' else [1, 28 * number],
            self.QUARTER: lambda number, calendar: [1, 3 * number],
            self.YEAR: lambda number, calendar: [1, 12 * number],
        }[self]

    @property
    def abbr(self):
        return {
            self.SECOND: 's',
            self.MINUTE: 'm',
            self.HOUR: 'h',
            self.DAY: 'd',
            self.WEEK: 'w',
        }[self]

    def __lt__(self, other):
        __order__ = [self.SECOND, self.MINUTE, self.HOUR, self.DAY, self.WEEK, self.MONTH, self.QUARTER, self.YEAR]
        return __order__.index(self) < __order__.index(other)


class HttpMethod(XuaEnum):
    GET = 'GET'
    POST = 'POST'


class ConfiguredCalendar:
    calendar = None

    @classmethod
    def set(cls, calendar):
        cls.calendar = calendar

    @classmethod
    def get(cls):
        return cls.calendar


class Time:
    def __init__(self, time: datetime = None):
        if time is None:
            self.second = 0
            self.minute = 0
            self.hour = 0
            self.day = 0
            self.month = 0
            self.quarter = 0
            self.year = 0
        else:
            self.second = time.second
            self.minute = time.minute
            self.hour = time.hour
            self.day = time.day
            self.month = time.month
            self.year = time.year

    def get_unit_value(self, unit: TimeUnit) -> int:
        return getattr(self, unit.value)

    def set_unit_value(self, unit: TimeUnit, value: int) -> None:
        self.__setattr__(unit.value, value)

    def equal_from_unit_to_end(self, other, *, unit: TimeUnit):
        while unit.has_below():
            unit = unit.below()
            if self.get_unit_value(unit) != other.get_unit_value(unit):
                return False
        return True

    def __str__(self):
        return f'{self.year}/{self.month}/{self.day}-{self.hour}:{self.minute}:{self.second}'

    @classmethod
    def now(cls):
        calendar = ConfiguredCalendar.get()
        if calendar == Calendar.GREGORIAN.value:
            now = datetime.datetime.now()
        elif calendar == Calendar.JALALI.value:
            now = jdatetime.datetime.now()
        else:
            raise Exception(f'Unknown calendar {calendar}')

        return cls(time=now)


class Occurrence:
    def __init__(self, raw_occurrence: str, parent_period):
        self.__raw_occurrence = self.__clean_raw_occurrence(raw_occurrence)

        self.__parent_period = parent_period

        self.time = self.__clean_time()

    @staticmethod
    def __clean_raw_occurrence(raw_occurrence) -> list:
        if type(raw_occurrence) is not str:
            raise UserError(f'Each period `occurrences` item must be a string.')

        if not raw_occurrence:
            return []

        try:
            return list(map(int, raw_occurrence.split(':')))
        except ValueError:
            raise UserError(f'Each period `occurrences` item must be integers seperated by colons.')

    def __clean_time(self) -> Time:
        raw_occurrence = self.__raw_occurrence

        time = Time()
        unit = self.__parent_period.unit
        for value in raw_occurrence:
            parent = unit
            if not unit.has_below():
                raise UserError(f"Value of occurrences {':'.join(list(map(str, raw_occurrence)))} has too many parts.")
            unit = unit.below()

            min_value, max_value = parent.limit_calculators()(self.__parent_period.number, ConfiguredCalendar.get())
            if not min_value <= value <= max_value:
                raise UserError(
                    f"Value of {value} must be between {min_value} and {max_value}.")

            time.set_unit_value(unit, value)

        return time

    @classmethod
    def zero(cls, parent_period):
        return cls('', parent_period)


class Period:
    def __init__(self, raw_period, *, allow_occurrences=False, max_unit=None):
        self.__raw_period = self.__clean_raw_period(raw_period)

        self.number = self.__clean_number()
        self.unit = self.__clean_unit(max_unit)
        self.occurrences = self.__clean_occurrences(allow_occurrences)

    @staticmethod
    def __clean_raw_period(raw_period) -> dict:
        if type(raw_period) is not dict:
            raise UserError(f'The period {raw_period} value must be a dict.')
        return raw_period

    def __clean_number(self) -> float:
        number = self.__raw_period.get('number', None)
        try:
            number = float(number)
        except ValueError:
            raise UserError(f'Value {number} is not a valid float/int number.')
        if number <= 0:
            raise UserError(f'Value {number} for period number must be positive.')
        return number

    def __clean_unit(self, max_unit) -> TimeUnit:
        unit_value = self.__raw_period.get('unit', None)
        try:
            unit = TimeUnit(unit_value)
        except ValueError:
            raise UserError(f'Value of {unit_value} must be in {TimeUnit.str()}.')
        if max_unit and unit > max_unit:
            raise UserError(f'Value of {unit} cannot be greater than {max_unit.value}.')
        return unit

    def __clean_occurrences(self, allow_occurrences) -> list:
        if not allow_occurrences and 'occurrences' in self.__raw_period:
            raise UserError(f'This period cannot contain `occurrences` directive.')

        raw_occurrences = self.__raw_period.get('occurrences', None)

        if raw_occurrences is None:
            return [Occurrence.zero(self)]

        if type(raw_occurrences) is not list:
            raise UserError(f'The period `occurrences` must be a list.')

        if not raw_occurrences:
            raise UserError(f'The period `occurrences` cannot be empty.')

        occurrences = []
        for occurrence in raw_occurrences:
            occurrences.append(Occurrence(occurrence, self))

        return occurrences


class LogsRotatingConfig:
    def __init__(self, raw_logs_rotating_config):
        self.__raw_logs_rotating_config = self.__clean_raw_logs_rotating_config(raw_logs_rotating_config)

        self.period = self.__clean_period()
        self.backup_count = self.__backup_count()

    @staticmethod
    def __clean_raw_logs_rotating_config(raw_logs_rotating_config):
        if type(raw_logs_rotating_config) is not dict:
            raise UserError('The logs rotating value must be a dict.')
        return raw_logs_rotating_config

    def __clean_period(self):
        period = self.__raw_logs_rotating_config.get('period', {})
        return Period(period, max_unit=TimeUnit.DAY)

    def __backup_count(self):
        backup_count = self.__raw_logs_rotating_config.get('backupCount', None)
        try:
            backup_count = int(backup_count)
        except ValueError:
            raise UserError(f'Value {backup_count} is not a valid float/int number.')
        if backup_count < 0:
            raise UserError(f'Value {backup_count} for rotating backupCount cannot be negative.')
        return backup_count


class LogsConfig:
    def __init__(self, raw_logs_config):
        self.__raw_logs_config = self.__clean_raw_logs_config(raw_logs_config)

        self.path = self.__clean_path()
        self.rotating = self.__clean_rotating()

    @staticmethod
    def __clean_raw_logs_config(raw_logs_config) -> dict:
        if type(raw_logs_config) is not dict:
            raise UserError('The logs value must be a dict.')
        return raw_logs_config

    def __clean_path(self) -> Path:
        path = self.__raw_logs_config.get('path', 'logs')
        if type(path) is not str:
            raise UserError(f'The logs directory {path} must be a string.')
        path = Path(path)
        return path

    def __clean_rotating(self) -> LogsRotatingConfig:
        rotating_config = self.__raw_logs_config.get('rotating', {})
        return LogsRotatingConfig(rotating_config)


class Server:
    def __init__(self, raw_server):
        self.__raw_server = self.__clean_raw_server(raw_server)

        self.base_url = self.__clean_base_url()
        self.headers = self.__clean_headers()
        self.logs = self.__clean_logs()

    @staticmethod
    def __clean_raw_server(raw_server) -> dict:
        if type(raw_server) is not dict:
            raise UserError('Each server must be a dict.')
        return raw_server

    def __clean_base_url(self) -> str:
        base_url = self.__raw_server.get('baseUrl', None)
        if type(base_url) is not str:
            raise UserError(f'Value {base_url} is not a valid url for server base url.')
        return base_url

    def __clean_logs(self) -> LogsConfig:
        logs = self.__raw_server.get('logs', {})
        return LogsConfig(logs)

    def __clean_headers(self):
        # @TODO read env
        headers_list = self.__raw_server.get('headers', [])
        if type(headers_list) is not list:
            raise UserError(f'Server headers must be a list.')

        headers = {}
        for header in headers_list:
            name_value = header.split(':')
            if len(name_value) != 2:
                raise UserError(f'Header value `{header}` must contain exactly one colon.')
            name, value = name_value
            headers[name] = os.path.expandvars(value.strip())

        return headers


class Job:
    def __init__(self, raw_job):
        self.__raw_job = self.__clean_raw_job(raw_job)

        self.resource = self.__clean_resource()
        self.method = self.__clean_method()
        self.request = self.__clean_request()
        self.allow_overlap = self.__clean_allow_overlap()
        self.store_logs = self.__clean_store_logs()
        self.run_on = self.__clean_run_on()
        self.period = self.__clean_period()

    @staticmethod
    def __clean_raw_job(raw_job) -> dict:
        if type(raw_job) is not dict:
            raise UserError('Each job must be a dict.')
        return raw_job

    def __clean_resource(self) -> str:
        resource = self.__raw_job.get('resource', None)
        if type(resource) is not str:
            raise UserError(f'Value {resource} is not a valid route.')
        return resource

    def __clean_method(self) -> HttpMethod:
        method = self.__raw_job.get('method', 'POST')
        if not HttpMethod.has_value(method):
            raise UserError(f'Value of {method} must be in {HttpMethod.str()}.')
        return HttpMethod(method)

    def __clean_request(self) -> dict:
        request = self.__raw_job.get('request', {})
        if type(request) is not dict:
            raise UserError(f'The request {request} value must be a dict.')
        return request

    def __clean_allow_overlap(self) -> bool:
        allow_overlap = self.__raw_job.get('allowOverlap', False)
        if type(allow_overlap) is not bool:
            raise UserError(f'The allowOverlap {allow_overlap} value must be a boolean.')
        return allow_overlap

    def __clean_store_logs(self) -> bool:
        store_logs = self.__raw_job.get('storeLogs', True)
        if type(store_logs) is not bool:
            raise UserError(f'The storeLogs {store_logs} value must be a boolean.')
        return store_logs

    def __clean_run_on(self) -> list:
        run_on = self.__raw_job.get('runOn', [])
        if type(run_on) is not list:
            raise UserError(f'The runOn {run_on} value must be a list.')
        return run_on

    def __clean_period(self):
        period = self.__raw_job.get('period', {})
        return Period(period, allow_occurrences=True)


class WorkerConfig:
    def __init__(self, config_path):
        os.chdir(Path(config_path).parent)
        self.__raw_config = self.__read_json_config(config_path)

        self.calendar = self.__clean_calendar()
        ConfiguredCalendar.set(self.calendar)
        self.servers = self.__clean_servers()
        self.jobs = self.__clean_jobs()

        self.__validate()

    @staticmethod
    def __read_json_config(config_path) -> dict:
        try:
            with open(config_path) as f:
                raw_config = json.load(f)
                if type(raw_config) is not dict:
                    raise UserError('The config dict.')
                return raw_config
        except FileNotFoundError:
            raise UserError(f'{config_path} not found.')
        except json.JSONDecodeError:
            raise UserError('Invalid json.')

    def __clean_calendar(self) -> dict:
        calendar = self.__raw_config.get('calendar', Calendar.GREGORIAN)
        if not Calendar.has_value(calendar):
            raise UserError(f'Value of {calendar} must be in {Calendar.str()}.')
        return calendar

    def __clean_servers(self) -> dict:
        raw_servers = self.__raw_config.get('servers', {})
        if type(raw_servers) is not dict:
            raise UserError('The servers value must be a dict.')
        servers = {}
        for server_name in raw_servers:
            servers[server_name] = Server(raw_servers[server_name])
        return servers

    def __clean_jobs(self) -> list:
        raw_jobs = self.__raw_config.get('jobs', [])
        if type(raw_jobs) is not list:
            raise UserError('The jobs value must be a list.')
        jobs = []
        for job in raw_jobs:
            jobs.append(Job(job))
        return jobs

    def __validate(self) -> None:
        self.__validate_run_on()

    def __validate_run_on(self) -> None:
        for job in self.jobs:
            run_on_set = set(job.run_on)
            servers_set = set(self.servers)
            if not (run_on_set <= servers_set):
                raise UserError(f'The values {run_on_set} value all be members of server name {servers_set}.')
