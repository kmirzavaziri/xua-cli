import os
import argparse
from xua.config import BuildConfig
from xua.constants import CONFIG, CLI, XUA
from xua import helpers, build_tools, xworker
from xua.exceptions import UserError


class XuaParser:
    @classmethod
    def parser(cls):
        parser = argparse.ArgumentParser(prog='xua')
        parser.add_argument('-v', '--version', action='store_true')
        subparsers = parser.add_subparsers(dest='service')

        cls.__new(subparsers)
        cls.__build(subparsers)
        cls.__worker(subparsers)

        return parser

    @classmethod
    def __new(cls, subparsers):
        parser = subparsers.add_parser(CLI.Services.NEW.value)
        parser.add_argument('type', choices=CLI.TEMPLATE_TYPE_)
        # @TODO

    @classmethod
    def __build(cls, subparsers):
        parser = subparsers.add_parser(CLI.Services.BUILD.value)
        parser.add_argument('project', choices=CLI.PROJECT_)
        parser.add_argument('path', type=str, nargs='?')
        parser.add_argument('-b', '--build-base', action='store_true')
        parser.add_argument('-c', '--changes', action='store_true')
        parser.add_argument('--build-dir', type=str, nargs='?')

    @classmethod
    def __worker(cls, subparsers):
        parser = subparsers.add_parser(CLI.Services.WORKER.value)
        parser.add_argument('config_path', type=str)


class Actor:
    @classmethod
    def main(cls, raw_args=None):
        args = XuaParser.parser().parse_args(raw_args)

        if args.version:
            print(XUA.HERO)
        elif args.service == CLI.Services.NEW.value:
            cls.__new(args)
        elif args.service == CLI.Services.BUILD.value:
            cls.__build(args)
        elif args.service == CLI.Services.WORKER.value:
            cls.__worker(args)
        else:
            print(XUA.HERO)

    @classmethod
    def __new(cls, args):
        raise UserError("Not implemented yet.")

    @classmethod
    def __build(cls, args):
        path = args.path if args.path else '.'
        if not os.path.exists(path):
            raise UserError(f"Path '{path}' does not exist.")
        path = os.path.abspath(path)

        root = helpers.getNearestDirContaining(path, CONFIG.XUA_JSON)
        if not root:
            raise UserError(
                f"Cannot find the file '{CONFIG.XUA_JSON}' in the root directory of the project.")

        os.chdir(root)
        path = os.path.relpath(path, root)

        config = BuildConfig(args)
        projects = config.getProjects()
        for project in projects:
            config.validations(project, path)

        for project in projects:
            buildEngine = build_tools.getBuildEngine(project, config)
            build_tools.buildRecursive(path, buildEngine)
            if args.build_base:
                buildEngine.buildBase()

    @classmethod
    def __worker(cls, args):
        xworker.WorkEngine.start(args.config_path)
