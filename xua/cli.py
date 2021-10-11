import os
import argparse
from xua.config import BuildConfig, WorkerConfig
from xua.constants import CONFIG, CLI, XUA
from xua import helpers, build_tools, work_tools
from xua.exceptions import UserError


def parser():
    # xua
    parser = argparse.ArgumentParser(prog='xua')
    parser.add_argument('-v', '--version', action='store_true')
    subparsers = parser.add_subparsers(dest='service')

    # xua new
    newParser = subparsers.add_parser(CLI.SERVICE_NEW)
    newParser.add_argument('type', choices=CLI.TEMPLATE_TYPE_)
    # @TODO

    # xua build
    buildParser = subparsers.add_parser(CLI.SERVICE_BUILD)
    buildParser.add_argument('project', choices=CLI.PROJECT_)
    buildParser.add_argument('path', type=str, nargs='?')
    buildParser.add_argument('-b', '--build-base', action='store_true')
    buildParser.add_argument('-c', '--changes', action='store_true')
    buildParser.add_argument('--build-dir', type=str, nargs='?')

    # xua worker
    workerParser = subparsers.add_parser(CLI.SERVICE_WORKER)
    workerParser.add_argument('config', type=str)
    workerParser.add_argument('base_url', type=str)
    workerParser.add_argument('-H', '--header', type=str, action='append')

    return parser


def entry(rawArgs=None):
    args = parser().parse_args(rawArgs)

    if args.version:
        print(XUA.HERO)
    elif args.service == CLI.SERVICE_NEW:
        new(args)
    elif args.service == CLI.SERVICE_BUILD:
        build(args)
    elif args.service == CLI.SERVICE_WORKER:
        worker(args)
    else:
        print(XUA.HERO)


def new(args):
    raise UserError("Not implemented yet.")


def build(args):
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
        if (args.build_base):
            buildEngine.buildBase()


def worker(args):
    config = WorkerConfig(args)
    workEngine = work_tools.WorkEngine(config)
    workEngine.start()
