from json.decoder import JSONDecodeError
import os
import json
from xua.constants import CLI, CONFIG, WORKER_CONFIG
from xua.exceptions import UserError
from xua import helpers


class BuildConfig:
    def __init__(self, args):
        self.cliArgs = args
        self.config = self.readConfig()

    def readConfig(self):
        with open(CONFIG.XUA_JSON) as f:
            config = json.load(f)
        default = CONFIG.VALUE.DEFAULT_()
        if CONFIG.KEY.PROJECTS not in config:
            raise UserError(
                f"'{CONFIG.XUA_JSON}' must contain key '{CONFIG.KEY.PROJECTS}'")
        for project in CONFIG.KEY.PROJECT_:
            if project in config[CONFIG.KEY.PROJECTS]:
                for key in CONFIG.KEY.PROJECT_KEY_[project]:
                    if key not in config[CONFIG.KEY.PROJECTS][project]:
                        try:
                            tmp = default[CONFIG.KEY.PROJECTS][project][key]
                        except KeyError:
                            raise UserError(
                                f"Key {CONFIG.KEY.PROJECTS}.{project}.{key} is required.")
                        if callable(tmp):
                            tmp = tmp(config)
                        config[CONFIG.KEY.PROJECTS][project][key] = tmp

                # @TODO generalize overrides
                if self.cliArgs.build_dir:
                    config[CONFIG.KEY.PROJECTS][project][CONFIG.KEY.BUILD_DIR] = self.cliArgs.build_dir

        return config

    def getProjects(self):
        project = self.cliArgs.project
        if project == CLI.PROJECT_INSTRUCTION_ALL:
            if self.cliArgs.build_dir:
                raise UserError('Cannot set --build-dir when project = all')
            projects = []
            for p in CONFIG.KEY.PROJECT_:
                if p in self.config[CONFIG.KEY.PROJECTS]:
                    projects.append(p)
            return projects
        elif project == CLI.PROJECT_INSTRUCTION_QUICK:
            if self.cliArgs.build_dir:
                raise UserError('Cannot set --build-dir when project = quick')
            projects = []
            for p in CONFIG.KEY.PROJECT_:
                if p in self.config[CONFIG.KEY.PROJECTS] and self.config[CONFIG.KEY.PROJECTS][p][CONFIG.KEY.QUICK]:
                    projects.append(p)
            return projects
        else:
            if project not in self.config[CONFIG.KEY.PROJECTS]:
                raise UserError(
                    f"The Xua project is not configured for '{project}'.")
        return [project]

    def validations(self, project, path):
        if not helpers.doesPathContainPath(self.config[CONFIG.KEY.PROJECTS][project][CONFIG.KEY.SRC_DIR], path):
            raise UserError(
                f"given path {path} is not in src-dir: {self.config[CONFIG.KEY.PROJECTS][project][CONFIG.KEY.SRC_DIR]}")

    def isToBuild(self, path, project):
        return path.endswith('.xua')

    def isToCopy(self, path, project):
        path = os.path.abspath(path)
        for pathToCopy in self.config[CONFIG.KEY.PROJECTS][project][CONFIG.KEY.PATHS_TO_COPY]:
            pathToCopy = os.path.abspath(os.path.join(
                self.config[CONFIG.KEY.PROJECTS][project][CONFIG.KEY.SRC_DIR], pathToCopy))
            if (
                (os.path.isfile(pathToCopy) and path == pathToCopy) or
                os.path.commonpath([pathToCopy]) == os.path.commonpath(
                    [pathToCopy, path])
            ):
                return True
            return False

    def getCorrespondingPath(self, project, path, extension=None):
        path = path if extension is None else os.path.splitext(path)[
            0] + extension
        return os.path.join(self.config[CONFIG.KEY.PROJECTS][project][CONFIG.KEY.BUILD_DIR], os.path.relpath(path, self.config[CONFIG.KEY.PROJECTS][project][CONFIG.KEY.SRC_DIR]))


class WorkerConfig:
    def __init__(self, args):
        self.cliArgs = args
        self.config = self.readConfig()

    def readConfig(self):
        try:
            with open(self.cliArgs.config) as f:
                config = json.load(f)
        except JSONDecodeError:
            raise UserError(f"Invalid json.")
        except FileNotFoundError:
            raise UserError(f"{self.cliArgs.config} not found.")

        default = WORKER_CONFIG.VALUE.DEFAULT_()

        for key in WORKER_CONFIG.KEY._:
            if key not in config:
                try:
                    tmp = default[key]
                except KeyError:
                    raise UserError(f"Key {key} is required.")
                config[key] = tmp

        # calendar validations
        if config[WORKER_CONFIG.KEY.CALENDAR] not in WORKER_CONFIG.VALUE.CALENDAR._:
            raise UserError(
                f"Value of {WORKER_CONFIG.KEY.CALENDAR} must be in ({', '.join(WORKER_CONFIG.VALUE.CALENDAR._)}).")

        # logs validations
        if type(config[WORKER_CONFIG.KEY.LOGS]) is not dict:
            raise UserError(
                f"Value of {WORKER_CONFIG.KEY.LOGS} must be a dict.")
        for key in WORKER_CONFIG.KEY.LOGS_:
            if key not in config[WORKER_CONFIG.KEY.LOGS]:
                try:
                    tmp = default[key]
                except KeyError:
                    raise UserError(
                        f"Key {WORKER_CONFIG.KEY.LOGS}.{key} is required.")
                config[WORKER_CONFIG.KEY.LOGS][key] = tmp

        # jobs validations
        if type(config[WORKER_CONFIG.KEY.JOBS]) is not list:
            raise UserError(
                f"Value of {WORKER_CONFIG.KEY.JOBS} must be a list.")
        for i, job in enumerate(config[WORKER_CONFIG.KEY.JOBS]):
            if type(job) is not dict:
                raise UserError(f"Value of each job must be a dict.")
            for key in WORKER_CONFIG.KEY.JOBS_:
                if key not in job:
                    try:
                        tmp = default[key]
                    except KeyError:
                        raise UserError(
                            f"Key {WORKER_CONFIG.KEY.JOBS}[{i}].{key} is required.")
                    config[WORKER_CONFIG.KEY.JOBS][i][key] = tmp

            # jobs.method validations
            if job[WORKER_CONFIG.KEY.JOBS_METHOD] not in WORKER_CONFIG.VALUE.JOBS_METHOD._:
                raise UserError(
                    f"Value of {WORKER_CONFIG.KEY.JOBS}[{i}].{WORKER_CONFIG.KEY.JOBS_METHOD} must be in ({', '.join(WORKER_CONFIG.VALUE.JOBS_METHOD._)}).")

            # jobs.every validations
            if type(job[WORKER_CONFIG.KEY.JOBS_EVERY]) is not dict:
                raise UserError(
                    f"Value of {WORKER_CONFIG.KEY.JOBS}[{i}].{WORKER_CONFIG.KEY.JOBS_EVERY} must be a dict.")
            for key in WORKER_CONFIG.KEY.JOBS_EVERY_:
                if key not in job[WORKER_CONFIG.KEY.JOBS_EVERY]:
                    try:
                        tmp = default[key]
                    except KeyError:
                        raise UserError(
                            f"Key {WORKER_CONFIG.KEY.JOBS}[{i}].{WORKER_CONFIG.KEY.JOBS_EVERY}.{key} is required.")
                    config[WORKER_CONFIG.KEY.JOBS][i][WORKER_CONFIG.KEY.JOBS_EVERY][key] = tmp

            # jobs.every.number validations
            if type(job[WORKER_CONFIG.KEY.JOBS_EVERY][WORKER_CONFIG.KEY.JOBS_EVERY_NUMBER]) is not int or job[WORKER_CONFIG.KEY.JOBS_EVERY][WORKER_CONFIG.KEY.JOBS_EVERY_NUMBER] <= 0:
                raise UserError(
                    f"Value of {WORKER_CONFIG.KEY.JOBS}[{i}].{WORKER_CONFIG.KEY.JOBS_EVERY}.{WORKER_CONFIG.KEY.JOBS_EVERY_NUMBER} must be a positive int.")

            # jobs.every.unit validations
            if job[WORKER_CONFIG.KEY.JOBS_EVERY][WORKER_CONFIG.KEY.JOBS_EVERY_UNIT] not in WORKER_CONFIG.VALUE.JOBS_EVERY_UNIT._:
                raise UserError(
                    f"Value of {WORKER_CONFIG.KEY.JOBS}[{i}].{WORKER_CONFIG.KEY.JOBS_EVERY}.{WORKER_CONFIG.KEY.JOBS_EVERY_UNIT} must be in ({', '.join(WORKER_CONFIG.VALUE.JOBS_EVERY_UNIT._)}).")

            # jobs.every.at validations
            if type(job[WORKER_CONFIG.KEY.JOBS_EVERY][WORKER_CONFIG.KEY.JOBS_EVERY_AT]) is not list:
                raise UserError(
                    f"Value of {WORKER_CONFIG.KEY.JOBS}[{i}].{WORKER_CONFIG.KEY.JOBS_EVERY}.{WORKER_CONFIG.KEY.JOBS_EVERY_AT} must be a list.")
            if job[WORKER_CONFIG.KEY.JOBS_EVERY][WORKER_CONFIG.KEY.JOBS_EVERY_AT] == []:
                raise UserError(
                    f"Value of {WORKER_CONFIG.KEY.JOBS}[{i}].{WORKER_CONFIG.KEY.JOBS_EVERY}.{WORKER_CONFIG.KEY.JOBS_EVERY_AT} cannot be empty.")
            for j, at in enumerate(job[WORKER_CONFIG.KEY.JOBS_EVERY][WORKER_CONFIG.KEY.JOBS_EVERY_AT]):
                ref = f"{WORKER_CONFIG.KEY.JOBS}[{i}].{WORKER_CONFIG.KEY.JOBS_EVERY}.{WORKER_CONFIG.KEY.JOBS_EVERY_AT}[{j}]"
                if type(at) is not str:
                    raise UserError(f"Value of {ref} must be a string.")
                try:
                    at = list(map(int, at.split(':')))
                except ValueError:
                    raise UserError(
                        f"Value of {ref} contains non-integer part between colons.")

                atDict = {}
                unit = job[WORKER_CONFIG.KEY.JOBS_EVERY][WORKER_CONFIG.KEY.JOBS_EVERY_UNIT]
                k = 0
                while unit in WORKER_CONFIG.VALUE.JOBS_EVERY_UNIT.LOWER:
                    parent = unit
                    unit = WORKER_CONFIG.VALUE.JOBS_EVERY_UNIT.LOWER[unit]
                    try:
                        atDict[unit] = at[k]
                    except IndexError:
                        atDict[unit] = 0

                    min, max = WORKER_CONFIG.VALUE.JOBS_EVERY_UNIT.AT_LIMIT[parent](
                        job[WORKER_CONFIG.KEY.JOBS_EVERY][WORKER_CONFIG.KEY.JOBS_EVERY_NUMBER], config[WORKER_CONFIG.KEY.CALENDAR])
                    if not min <= atDict[unit] <= max:
                        raise UserError(
                            f"Value of {ref} part {k} must be between {min} and {max}.")

                    k += 1

                if k < len(at) and job[WORKER_CONFIG.KEY.JOBS_EVERY][WORKER_CONFIG.KEY.JOBS_EVERY_UNIT] != WORKER_CONFIG.VALUE.JOBS_EVERY_UNIT.SECOND:
                    raise UserError(f"Value of {ref} contains too many parts.")

                config[WORKER_CONFIG.KEY.JOBS][i][WORKER_CONFIG.KEY.JOBS_EVERY][WORKER_CONFIG.KEY.JOBS_EVERY_AT][j] = atDict

        return config
