import os
import argparse
import json
import xuadoc


class XuaTools:
    rootdir = ""
    config = None

    def __init__(self, rootdir):
        self.rootdir = rootdir
        os.chdir(self.rootdir)
        with open("config.json") as f:
            text = f.read()
        self.setConfig(text)

    @staticmethod
    def xuaArgParse():
        parser = argparse.ArgumentParser(prog='xua')
        parser.add_argument('service', choices=['build', 'new'])
        parser.add_argument('args', action='append', nargs='*')

        return parser.parse_args()

    @staticmethod
    def xuaBuildArgParse(args):
        parser = argparse.ArgumentParser(prog='xua build')
        parser.add_argument('filename', type=str, nargs='?')
        return parser.parse_args(args)

    @staticmethod
    def getProjectDir(name):
        if os.path.isdir(name):
            name = os.path.join(name, 'virtual_file_name.ext')
        while name != os.path.dirname(name):
            name = os.path.dirname(name)
            if '.__xua_root__' in os.listdir(name):
                return name
        return

    def setConfig(self, configStr):
        self._config = json.loads(configStr)

        if 'settings' not in self._config:
            self._config['settings'] = {}

        if 'php' not in self._config['settings']:
            self._config['settings']['php'] = {}

        if 'doc' not in self._config['settings']:
            self._config['settings']['doc'] = {}

    def write(self, content, relativerootdir, name, ext):
        name = os.path.join(
            self.rootdir,
            relativerootdir,
            os.path.splitext(name)[0] + ext
        )
        os.makedirs(os.path.dirname(name), exist_ok=True)
        with open(name, 'w') as f:
            f.write(content)

    def build(self, filename):
        relativeFilename = filename[len(self.rootdir)+1:]
        if (self._config['settings']['php']):
            self.write(
                self.buildPhp(filename),
                self._config['settings']['php']['destination-dir'],
                relativeFilename,
                '.php'
            )
        if (self._config['settings']['doc']):
            if (self._config['settings']['doc']['latex']):
                self.write(
                    self.buildDoc(filename, 'latex'),
                    self._config['settings']['doc']['latex']['destination-dir'],
                    relativeFilename,
                    '.tex'
                )
            if (self._config['settings']['doc']['html']):
                self.write(
                    self.buildDoc(filename, 'html'),
                    self._config['settings']['doc']['html']['destination-dir'],
                    relativeFilename,
                    '.html'
                )

        return

    def buildPhp(self, filename):
        # @TODO
        return ''

    def buildDoc(self, filename, format):
        if format == 'html':
            return xuadoc.HtmlGenerator(filename, self._config).render()
        elif format == 'latex':
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
