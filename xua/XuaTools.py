import os
import argparse
import json
import xuadoc
from shutil import copyfile
from XuaLogger import XuaLogger as XL

class XuaTools:
    STACK_SERVER_PHP   = 'server/php'
    STACK_MARSHAL_DART = 'marshal/dart'
    STACK_DOC_HTML     = 'doc/html'
    STACK_DOC_LATEX    = 'doc/latex'
    STACK_ = [
        STACK_SERVER_PHP,
        STACK_MARSHAL_DART,
        STACK_DOC_HTML,
        STACK_DOC_LATEX,
    ]

    MAP_STACK_EXTENSION = {
        STACK_SERVER_PHP: '.php',
        STACK_MARSHAL_DART: '.dart',
        STACK_DOC_HTML: '.html',
        STACK_DOC_LATEX: '.tex',
    }

    rootdir = ""
    config = None

    def __init__(self, rootdir):
        self.rootdir = rootdir
        os.chdir(self.rootdir)
        with open('config.json') as f:
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

        if 'stacks' not in self._config:
            self._config['stacks'] = {}

        for stack in XuaTools.STACK_:
            if stack not in self._config['stacks']:
                self._config['stacks'][stack] = {}

    def getCorrespondingPath(self, stack, filename, newExtension = None):
        filename = filename if newExtension is None else os.path.splitext(filename)[0] + newExtension
        return os.path.join(self.rootdir, self._config['stacks'][stack]['destination-dir'], filename)

    def copy(self, source, destination):
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        copyfile(source, destination)

    def write(self, content, destination):
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        with open(destination, 'w') as f:
            f.write(content)

    def build(self, filename):
        filename = filename[len(self.rootdir)+1:]
        for stack in XuaTools.STACK_:
            if self._config['stacks'][stack]:
                XL.log(XL.INFO, stack, 'READING', filename)
                try:
                    if filename.endswith('.xua'):
                        destination = self.getCorrespondingPath(stack, filename, XuaTools.MAP_STACK_EXTENSION[stack])
                        self.write(self._build(filename, stack), destination)
                    elif any([filename.startswith(resource + (os.sep if resource[-1] != os.sep else '')) or filename == resource for resource in self._config['stacks'][stack]['resources']]):
                        destination = self.getCorrespondingPath(stack, filename)
                        self.copy(filename, destination)
                    else:
                        XL.log(XL.WARNING, stack, 'OMITING', filename)
                except Exception as e:
                    XL.log(XL.ERROR, stack, 'FAILED WITH MESSAGE', str(e))
                else:
                    XL.log(XL.SUCCESS, stack, 'BUILT INTO', filename)
        return

    def _build(self, filename, stack):
        if stack == XuaTools.STACK_SERVER_PHP:
            return self.buildServerPhp(filename)
        elif stack == XuaTools.STACK_MARSHAL_DART:
            return self.buildMarshalDart(filename)
        elif stack == XuaTools.STACK_DOC_HTML:
            return self.buildDocHtml(filename)
        elif stack == XuaTools.STACK_DOC_LATEX:
            return self.buildDocLatex(filename)
        else:
            raise Exception(f'Unknown stack {stack}')
    
    def buildServerPhp(self, filename):
        # @TODO
        return ''

    def buildDocHtml(self, filename):
        return xuadoc.HtmlGenerator(filename, self._config).render()

    def buildDocLatex(self, filename):
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
