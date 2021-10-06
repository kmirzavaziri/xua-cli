import re
import os
import shutil
import html
from xua.constants import CONFIG

SINGLE_QUOTE = "'"

class Doc:
    # def toc(self, list):
    #     result = ''
    #     for item in list:
    #         result += filename
    #     return result
    pass


class DynamicClass:
    pass


class ReMatcher(object):
    def __init__(self, matchstring):
        self.matchstring = matchstring

    def match(self, regexp):
        self.rematch = re.match(regexp, self.matchstring)
        return bool(self.rematch)

    def group(self, i):
        return self.rematch.group(i)


class HtmlGenerator:
    def __init__(self, filename, config):
        self._config = config
        self._BLOCK_MODE_CODE = "code"
        self._BLOCK_MODE_COMMENT = "comment"

        self._BLOCK_MODES = [
            self._BLOCK_MODE_CODE,
            self._BLOCK_MODE_COMMENT,
        ]

        self._RENDER_MODE_PURE = "pure"
        self._RENDER_MODE_DOC = "doc"
        self._RENDER_MODE_NONE = "none"

        self._RENDER_MODES = [
            self._RENDER_MODE_PURE,
            self._RENDER_MODE_DOC,
            self._RENDER_MODE_NONE,
        ]

        self._SYMBOL_NAME_RE_GROUP = r"([a-zA-Z_][a-zA-Z_0-9]*)"

        self._properties = DynamicClass()
        self._properties.doc = Doc()
        self._properties.doc.renderComments = self._RENDER_MODE_NONE
        self._properties.doc.renderCodes = self._RENDER_MODE_DOC
        self._properties.doc.htmlTemplate = self._config[CONFIG.KEY.PROJECTS][CONFIG.KEY.PROJECT_DOC_HTML][CONFIG.KEY.DEFAULT_TEMPLATE] or 'template.html'
        self._properties.doc.constants = DynamicClass()
        self._properties.doc.content = ''

        self.warnings = []

        self._blocks = [
            {
                "mode": self._BLOCK_MODE_CODE,
                "content": ""
            }
        ]

        self._filename = filename

        with open(filename) as f:
            self._statements = f.read().splitlines()

        self._read()

    def _read(self):
        for statement in self._statements:
            m = ReMatcher(statement)

            ###############################
            # comment line
            if (m.match(r"\s*#\s*(.*)")):
                commentContent = m.group(1)
                m = ReMatcher(commentContent)

                # double comment
                if (m.match(r"--.*")):
                    # Do nothing
                    pass

                # python code
                elif (m.match(r"@python \s*(.*)")):
                    exec(m.group(1), {}, self._properties.__dict__)

                # comment
                else:
                    if self._properties.doc.renderComments == self._RENDER_MODE_PURE:
                        self._appendCode(statement)
                    elif self._properties.doc.renderComments == self._RENDER_MODE_DOC:
                        m = ReMatcher(statement)
                        if (m.match(r"\s*#(    |\t)(.*)")):
                            self._appendCode(m.group(2))
                        else:
                            self._appendComment("\n" + commentContent)
                    elif self._properties.doc.renderComments == self._RENDER_MODE_NONE:
                        # Do nothing
                        pass

            ###############################
            # code line
            else:
                if self._properties.doc.renderCodes == self._RENDER_MODE_PURE:
                    self._appendCode(statement)
                elif self._properties.doc.renderCodes == self._RENDER_MODE_DOC:
                    # TODO
                    pass
                elif self._properties.doc.renderCodes == self._RENDER_MODE_NONE:
                    # Do nothing
                    pass

    def render(self):
        with open(self._properties.doc.htmlTemplate, 'r') as f:
            template = f.read()

        doc = ""
        for block in self._blocks:
            if block["content"]:
                if block["mode"] == self._BLOCK_MODE_CODE:
                    doc += "<pre><code>" + block["content"] + "</code></pre>"
                else:
                    doc += "<div class = '" + \
                        block["mode"] + "'>" + \
                        self._html(block["content"]) + "</div>"

        content = self._properties.doc.content if self._properties.doc.content != '' else doc
        result = re.sub(r"\{\{\s*XUA-DOC-HOLDER\s*\}\}",
                        content.replace('\\', '\\\\'), template)

        rootRelativePath = os.path.relpath('.', start=os.path.dirname(self._filename))
        result = re.sub(r"\{\{\s*ROOT\s*\}\}", rootRelativePath, result)

        result = re.sub(
            r'%\s*' + self._SYMBOL_NAME_RE_GROUP + '\s*(\?\?\s*(.*))?\s*%',
            lambda x:
                self._properties.doc.constants.__dict__[x[1]]
                if x[1] in self._properties.doc.constants.__dict__
                else x[3],
            result
        )

        return result

    def getToc(self):
        # TODO
        return []

    def _appendCode(self, statement):
        statement = html.escape(statement)
        statement = statement.replace("\t", "    ")
        statement = statement.replace(" ", "&nbsp;")
        statement += "<br>" if statement.strip() != "" else ""
        if self._blocks[-1]["mode"] == self._BLOCK_MODE_CODE:
            self._blocks[-1]["content"] += statement
        if self._blocks[-1]["mode"] == self._BLOCK_MODE_COMMENT:
            self._blocks.append(
                {
                    "mode": self._BLOCK_MODE_CODE,
                    "content": statement
                }
            )

    def _appendComment(self, statement):
        if self._blocks[-1]["mode"] == self._BLOCK_MODE_COMMENT:
            self._blocks[-1]["content"] += statement
        if self._blocks[-1]["mode"] == self._BLOCK_MODE_CODE:
            self._blocks.append(
                {
                    "mode": self._BLOCK_MODE_COMMENT,
                    "content": statement
                }
            )

    def _html(self, statement):
        statement = statement.strip()

        # latex
        # statement = re.sub(
        #     r"\$(((?!\$).)*)\$",
        #     r"\(\1\)",
        #     statement
        # )

        # Bold
        statement = re.sub(
            r"\*\*(((?!\*\*).)*)\*\*",
            r"<strong>\1</strong>",
            statement
        )

        statement = re.sub(
            r"__(((?!__).)*)__",
            r"<strong>\1</strong>",
            statement
        )

        # Italic
        statement = re.sub(
            r"\*(((?!\*).)*)\*",
            r"<em>\1</em>",
            statement
        )

        statement = re.sub(
            r"([^\\])?_(((?!_).)*)_",
            r"\1<em>\2</em>",
            statement
        )

        # Inline Code
        statement = re.sub(
            r"`(((?!(?<!\\)`).)*)`",
            lambda x: "<code>" +
            html.escape(x.group(1).replace(r"\`", "`")) + "</code>",
            statement
        )

        # Image
        statement = re.sub(
            r"\!\[([^\]]*)\]\s*\(([^)\s]*)(\s+=(\d+)x(\d+)?)?\)",
            lambda x: f"<img class='figure' alt='{x.group(1)}' src='{x.group(2)}' width='{x.group(4)}'{f' height={SINGLE_QUOTE + x.group(5) + SINGLE_QUOTE}' if x.group(5) else ''}>",
            statement
        )

        # Link
        statement = re.sub(
            r"\[([^\]]*)\]\s*\(([^\)]*)\)",
            lambda x: "<a href='" +
            x.group(2).strip().replace(r'\(', '(').replace(r'\)', ')') +
            "'>" +
            x.group(1).replace(r'\[', '[').replace(r'\]', ']') +
            "</a>",
            statement
        )

        # h6
        statement = re.sub(
            r"^######(.*)",
            lambda x: "<a href='#" + x.group(1).strip().replace(' ', '_') + "'><h6 class='h6' id='" + x.group(
                1).strip().replace(' ', '_') + "'>" + x.group(1) + "</h6></a>",
            statement
        )

        # h5
        statement = re.sub(
            r"^#####(.*)",
            lambda x: "<a href='#" + x.group(1).strip().replace(' ', '_') + "'><h5 class='h5' id='" + x.group(
                1).strip().replace(' ', '_') + "'>" + x.group(1) + "</h5></a>",
            statement
        )

        # h4
        statement = re.sub(
            r"^####(.*)",
            lambda x: "<a href='#" + x.group(1).strip().replace(' ', '_') + "'><h4 class='h4' id='" + x.group(
                1).strip().replace(' ', '_') + "'>" + x.group(1) + "</h4></a>",
            statement
        )

        # h3
        statement = re.sub(
            r"^###(.*)",
            lambda x: "<a href='#" + x.group(1).strip().replace(' ', '_') + "'><h3 class='h3' id='" + x.group(
                1).strip().replace(' ', '_') + "'>" + x.group(1) + "</h3></a>",
            statement
        )

        # h2
        statement = re.sub(
            r"^##(.*)",
            lambda x: "<a href='#" + x.group(1).strip().replace(' ', '_') + "'><h2 class='h2' id='" + x.group(
                1).strip().replace(' ', '_') + "'>" + x.group(1) + "</h2></a>",
            statement
        )

        # h1
        statement = re.sub(
            r"^#(.*)",
            lambda x: "<a href='#" + x.group(1).strip().replace(' ', '_') + "'><h1 class='h1' id='" + x.group(
                1).strip().replace(' ', '_') + "'>" + x.group(1) + "</h1></a>",
            statement
        )

        # Unordered List
        # TODO

        # List
        # TODO

        # Table
        def table(x):
            width = None
            rows = []
            for row in x.group(0).strip().splitlines():
                row = row.split('|')[1:-1]
                row = [cell.strip() for cell in row]
                if width is None:
                    width = len(row)
                else:
                    if width != len(row):
                        return x.group(0)
                rows.append(row)
            directions = []
            for cell in rows[1]:
                direction = ''
                if cell.startswith(':') and cell.endswith(':'):
                    direction = 'center'
                if cell.startswith(':') and not cell.endswith(':'):
                    direction = 'left'
                if not cell.startswith(':') and cell.endswith(':'):
                    direction = 'right'
                if not cell.startswith(':') and not cell.endswith(':'):
                    direction = 'left'
                directions.append(direction)
            del rows[1]
            head = rows[0]
            del rows[0]
            return f"""
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            {" ".join([f"<th style='text-align: {directions[i]}'>{head[i]}</th>" for i in range(width)])}
                        </tr>
                    </thead>
                    <tbody>
                        {" ".join(["<tr>" + " ".join([f"<td style='text-align: {directions[i]}'>{row[i]}</td>" for i in range(width)]) + "</tr>" for row in rows])}
                    </tbody>
                </table>
            """
        statement = re.sub(
            r"(\s*\|(.*\|)+\s*)(\s*\|(\s*:?---+:?\s*\|)+\s*)(\s*\|(.*\|)+\s*)*",
            table,
            statement
        )

        return statement
