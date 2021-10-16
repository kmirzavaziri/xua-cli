import os
from xua import helpers
from xua.constants import CLI, BUILD
from xua.exceptions import UserError
from xua.builders.doc import html


def getBuildEngine(project, config):
    if project == CLI.PROJECT_SERVER_PHP:
        # @TODO
        return None
    elif project == CLI.PROJECT_MARSHAL_DART:
        # @TODO
        return None
    elif project == CLI.PROJECT_DOC_HTML:
        return html.BuildEngine(config)
    elif project == CLI.PROJECT_DOC_LATEX:
        # @TODO
        return None
    else:
        raise UserError(f"Unknown project {project}.")


def buildRecursive(path, buildEngine):
    if os.path.isfile(path):
        if buildEngine.config.isToBuild(path, buildEngine.project):
            destination = buildEngine.config.getCorrespondingPath(
                buildEngine.project, path, BUILD.MAP_PROJECT_EXTENSION[buildEngine.project])
            try:
                helpers.write(buildEngine.build(path), destination)
            except UserError as e:
                helpers.Logger.log(helpers.Logger.ERROR,
                                   buildEngine.project, path + ": " + str(e))
            else:
                helpers.Logger.log(helpers.Logger.SUCCESS,
                                   buildEngine.project, destination + ' built.')
        elif buildEngine.config.isToCopy(path, buildEngine.project):
            helpers.copy(path, buildEngine.config.getCorrespondingPath(
                buildEngine.project, path))
    elif os.path.isdir(path):
        for child in os.listdir(path):
            buildRecursive(os.path.join(path, child), buildEngine)
