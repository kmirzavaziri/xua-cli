import os
import argparse
import json
from shutil import copyfile
from xua.constants import CONFIG, CLI, XUA
import xua.doc

class Logger:
    INFO    = 'INFO'
    WARNING = 'WARNING'
    ERROR   = 'ERROR'
    SUCCESS = 'SUCCESS'

    class Format:
        BLACK         = '\033[30m'
        RED           = '\033[31m'
        GREEN         = '\033[32m'
        YELLOW        = '\033[33m'
        BLUE          = '\033[34m'
        MAGENTA       = '\033[35m'
        CYAN          = '\033[36m'
        LIGHT_GRAY    = '\033[37m'
        DARK_GRAY     = '\033[90m'
        LIGHT_RED     = '\033[91m'
        LIGHT_GREEN   = '\033[92m'
        LIGHT_YELLOW  = '\033[93m'
        LIGHT_BLUE    = '\033[94m'
        LIGHT_MAGENTA = '\033[95m'
        LIGHT_CYAN    = '\033[96m'
        WHITE         = '\033[97m'

        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'

        @staticmethod
        def format(text, format):
            return format + text + Logger.Format.END

    @staticmethod
    def log(type, stack, message):
        typeText = f'{type: <7}'
        if (type == Logger.INFO):
            typeText = Logger.Format.format(typeText, Logger.Format.BOLD + Logger.Format.LIGHT_BLUE)
        elif (type == Logger.WARNING):
            typeText = Logger.Format.format(typeText, Logger.Format.BOLD + Logger.Format.LIGHT_YELLOW)
        elif (type == Logger.ERROR):
            typeText = Logger.Format.format(typeText, Logger.Format.BOLD + Logger.Format.LIGHT_RED)
        elif (type == Logger.SUCCESS):
            typeText = Logger.Format.format(typeText, Logger.Format.BOLD + Logger.Format.LIGHT_GREEN)

        stackText = f'{stack: <12}'
        stackText = Logger.Format.format(stackText, Logger.Format.MAGENTA)
        print(f'{typeText} {stackText} {Logger.Format.format(message, Logger.Format.LIGHT_GRAY)}')

class UserError(Exception):
    pass

class Cli:
    @staticmethod
    def parser():
        # xua
        parser = argparse.ArgumentParser(prog='xua')
        subparsers = parser.add_subparsers(dest='service')

        # xua new
        newParser = subparsers.add_parser(CLI.SERVICE_NEW)
        newParser.add_argument('type', choices=CLI.TEMPLATE_TYPE_)
        # @TODO

        # xua build
        buildParser = subparsers.add_parser(CLI.SERVICE_BUILD)
        buildParser.add_argument('project', choices=CLI.PROJECT_)
        buildParser.add_argument('path', type=str, nargs='?')
        buildParser.add_argument('-c', '--changes', action='store_true')
        buildParser.add_argument('--build-dir', type=str, nargs='?')

        return parser

    @staticmethod
    def entry(rawArgs = None):
        args = Cli.parser().parse_args(rawArgs)

        if args.service == CLI.SERVICE_BUILD:
            Cli.build(args)
        elif args.service == CLI.SERVICE_NEW:
            Cli.new(args)
        else:
            print(XUA.HERO)

    @staticmethod
    def build(args):
        path = args.path if args.path else '.'
        if not os.path.exists(path):
            raise UserError(f"Path '{path}' does not exist.")
        path = os.path.abspath(path)

        root = Helper.getNearestDirContaining(path, CONFIG.XUA_JSON)
        if not root:
            raise UserError(f"Cannot find the file '{CONFIG.XUA_JSON}' in the root directory of the project.")

        os.chdir(root)
        path = os.path.relpath(path, root)

        builder = Builder(args)
        projects = builder.getProjects(args.project)
        for project in projects:
            builder.build(project, path)

    @staticmethod
    def new(args):
        raise UserError("Not implemented yet.")

class Helper:
    @staticmethod
    def getNearestDirContaining(path, containing):
        if os.path.isfile(path):
            path = os.path.dirname(path)
        while True:
            if containing in os.listdir(path):
                return path
            if path == os.path.dirname(path):
                return None
            path = os.path.dirname(path)

    @staticmethod
    def copy(source, destination):
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        copyfile(source, destination)

    @staticmethod
    def write(content, destination):
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, 'w') as f:
            f.write(content)

class Builder:
    MAP_PROJECT_EXTENSION = {
        CLI.PROJECT_SERVER_PHP: '.php',
        CLI.PROJECT_MARSHAL_DART: '.dart',
        CLI.PROJECT_DOC_HTML: '.html',
        CLI.PROJECT_DOC_LATEX: '.tex',
    }
    def __init__(self, args):
        self.cliArgs = args
        self.readConfig()

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
        self.config = config

    def getProjects(self, project):
        if project == CLI.PROJECT_INSTRUCTION_ALL:
            projects = []
            for p in CONFIG.KEY.PROJECT_:
                if p in self.config[CONFIG.KEY.PROJECTS]:
                    projects.append(p)
            return projects
        elif project == CLI.PROJECT_INSTRUCTION_QUICK:
            projects = []
            for p in CONFIG.KEY.PROJECT_:
                if p in self.config[CONFIG.KEY.PROJECTS] and self.config[CONFIG.KEY.PROJECTS][p][CONFIG.KEY.QUICK]:
                    projects.append(p)
            return projects
        else:
            if project not in self.config[CONFIG.KEY.PROJECTS]:
                raise UserError(f"The Xua project is not configured for '{project}'.")
        return [project]

    def build(self, project, path):
        if os.path.isfile(path):
            if self.isToBuild(path, project):
                destination = self.getCorrespondingPath(project, path, Builder.MAP_PROJECT_EXTENSION[project])
                try:
                    Helper.write(self._build(project, path), destination)
                except UserError as e:
                    Logger.log(Logger.ERROR, project, path + ": " + str(e))        
                else:
                    Logger.log(Logger.SUCCESS, project, destination + ' built.')
            elif self.isToCopy(path, project):
                Helper.copy(path, self.getCorrespondingPath(project, path))
        elif os.path.isdir(path):
            for child in os.listdir(path):
                self.build(project, os.path.join(path, child))

    def _build(self, project, path):
        if project == CLI.PROJECT_SERVER_PHP:
            return self._serverPhp(path)
        elif project == CLI.PROJECT_MARSHAL_DART:
            return self._marshalDart(path)
        elif project == CLI.PROJECT_DOC_HTML:
            return self._docHtml(path)
        elif project == CLI.PROJECT_DOC_LATEX:
            return self._docLatex(path)

    def isToBuild(self, path, project):
        return path.endswith('.xua')

    def isToCopy(self, path, project):
        path = os.path.abspath(path)
        for pathToCopy in self.config[CONFIG.KEY.PROJECTS][project][CONFIG.KEY.PATHS_TO_COPY]:
            pathToCopy = os.path.abspath(pathToCopy)
            if (
                (os.path.isfile(pathToCopy) and path == pathToCopy) or
                os.path.commonpath([pathToCopy]) == os.path.commonpath([pathToCopy, path])
            ):
                return True
            return False

    def getCorrespondingPath(self, project, path, extension = None):
        buildDir = self.cliArgs.build_dir if self.cliArgs.build_dir else self.config[CONFIG.KEY.PROJECTS][project][CONFIG.KEY.BUILD_DIR]
        path = path if extension is None else os.path.splitext(path)[0] + extension
        return os.path.join(buildDir, path)

    def _serverPhp(self, filename):
        # @TODO
        return ''

    def _marshalDart(self, filename):
        # @TODO
        return ''

    def _docHtml(self, filename):
        return xua.doc.HtmlGenerator(filename, self.config).render()

    def _docLatex(self, filename):
        # @TODO
        return ''

    # def fixBookConfig(configRoot):
    #     # Fix settings
    #     if configRoot.find("settings"):
    #         configRoot.append(ET.fromstring("""
    #             <settings>
    #                 <formats>
    #                     <html template=""" +  + """ pdf="false" />
    #                 </formats>
    #                 <toc name="TOC" template="toc-template.html">
    #                     <exclude-headings>
    #                         <heading order="3" />
    #                         <heading order="4" />
    #                         <heading order="5" />
    #                         <heading order="6" />
    #                     </exclude-headings>
    #                     <exclude-chapters>
    #                         <chapter name="Architecture" />
    #                     </exclude-chapters>
    #                 </toc>
    #             </settings>
    #         """))

    # def getDefaultBookTemplate(formatName):
    #     if formatName == "html":
    #         return dir_path + os.path.sep + "template.html"

    # def generateTocText(toc):
    #     tocText = "# xuadoc.renderComments = 'doc'\n# xuadoc.renderCodes = 'pure'\n"
    #     for item in toc:
    #         tocText += "# [" + item["label"] + "](" + item["url"] + ")\n\n"
    #     return tocText