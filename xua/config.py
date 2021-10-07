import os
import json
from xua.constants import CONFIG, CLI
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
            raise UserError(f"'{CONFIG.XUA_JSON}' must contain key '{CONFIG.KEY.PROJECTS}'")
        for project in CONFIG.KEY.PROJECT_:
            if project in config[CONFIG.KEY.PROJECTS]:
                for key in CONFIG.KEY.PROJECT_KEY_[project]:
                    if key not in config[CONFIG.KEY.PROJECTS][project]:
                        try:
                            tmp = default[CONFIG.KEY.PROJECTS][project][key]
                        except KeyError:
                            raise UserError(f"Key {CONFIG.KEY.PROJECTS}.{project}.{key} is required.")
                        if callable(tmp):
                            tmp = tmp(config)
                        config[CONFIG.KEY.PROJECTS][project][key] = tmp
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
                raise UserError(f"The Xua project is not configured for '{project}'.")
        return [project]

    def validations(self, project, path):
        if not helpers.doesPathContainPath(self.config[CONFIG.KEY.PROJECTS][project][CONFIG.KEY.SRC_DIR], path):
            raise UserError(f"given path {path} is not in src-dir: {self.config[CONFIG.KEY.PROJECTS][project][CONFIG.KEY.SRC_DIR]}")

    def isToBuild(self, path, project):
        return path.endswith('.xua')

    def isToCopy(self, path, project):
        path = os.path.abspath(path)
        for pathToCopy in self.config[CONFIG.KEY.PROJECTS][project][CONFIG.KEY.PATHS_TO_COPY]:
            pathToCopy = os.path.abspath(os.path.join(self.config[CONFIG.KEY.PROJECTS][project][CONFIG.KEY.SRC_DIR], pathToCopy))
            if (
                (os.path.isfile(pathToCopy) and path == pathToCopy) or
                os.path.commonpath([pathToCopy]) == os.path.commonpath([pathToCopy, path])
            ):
                return True
            return False

    def getCorrespondingPath(self, project, path, extension = None):
        buildDir = self.cliArgs.build_dir if self.cliArgs.build_dir else self.config[CONFIG.KEY.PROJECTS][project][CONFIG.KEY.BUILD_DIR]
        path = path if extension is None else os.path.splitext(path)[0] + extension
        return os.path.join(buildDir, os.path.relpath(path, self.config[CONFIG.KEY.PROJECTS][project][CONFIG.KEY.SRC_DIR]))