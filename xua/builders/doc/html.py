import os
from weasyprint import HTML
from xua.builders.eve import BuildEngineEve
from xua.constants import CONFIG, BUILD
from xua.builders.doc.yacc import parse
from xua.builders.doc import helpers


class engine(BuildEngineEve):
    # Eve Methods
    def __init__(self, config):
        super().__init__(config)
        self.toc = {}
        linear = helpers.TocNode.getNodes(config)
        for node in linear:
            self.toc[node.path] = node

    def _project(self):
        return CONFIG.KEY.PROJECT_DOC_HTML

    def _build(self, path):
        # level = self.toc[path].level if path in self.toc else path.count(os.path.sep)
        with open(path, 'r') as f:
            source = f.read()
        comments = self._getComments(source)
        # tokens = tokenize(comments)
        tree = parse(comments)

        return str(tree)

    def _buildBase(self):
        self.__buildPdf()

    # New Methods
    def _getComments(self, source):
        comments = []
        sourceLines = source.splitlines()
        for i in range(len(sourceLines)):
            hashIndex = sourceLines[i].find('#')
            comment = sourceLines[i][hashIndex + 1:] if hashIndex >= 0 else ''
            if i > 0 and sourceLines[i - 1] and sourceLines[i - 1][-1] == '\\':
                comments[-1] += '\n' + comment
            else:
                comments.append(comment)
        return '\n'.join(comments)

    def __buildPdf(self):
        if CONFIG.KEY.PDF_PATH not in self.config.config[CONFIG.KEY.PROJECTS][CONFIG.KEY.PROJECT_DOC_HTML]:
            return

        pdfPath = os.path.join(self.config.config[CONFIG.KEY.PROJECTS][CONFIG.KEY.PROJECT_DOC_HTML][CONFIG.KEY.BUILD_DIR],
                               self.config.config[CONFIG.KEY.PROJECTS][CONFIG.KEY.PROJECT_DOC_HTML][CONFIG.KEY.PDF_PATH])

        book = ''
        for node in self.toc:
            with open(self.config.getCorrespondingPath(CONFIG.KEY.PROJECT_DOC_HTML, node, BUILD.MAP_PROJECT_EXTENSION[CONFIG.KEY.PROJECT_DOC_HTML])) as f:
                book += f.read()

        HTML(string=book, base_url=self.config.config[CONFIG.KEY.PROJECTS]
             [CONFIG.KEY.PROJECT_DOC_HTML][CONFIG.KEY.BUILD_DIR]).write_pdf(pdfPath)
