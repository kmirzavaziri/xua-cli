from xua import helpers
from xua.constants import CONFIG

class BuildEngineEve:
    def __init__(self, config):
        self.config = config
        self.project = self._project()

    def build(self, path):
        r = self._build(path)
        return r

    def buildBase(self):
        r = self._buildBase()
        helpers.Logger.log(helpers.Logger.SUCCESS, CONFIG.KEY.PROJECT_DOC_HTML, helpers.Logger.Format.format('Base built.', helpers.Logger.Format.LIGHT_CYAN))
        return r