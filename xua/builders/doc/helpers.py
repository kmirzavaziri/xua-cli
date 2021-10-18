import os
from xua.exceptions import UserError
from xua.constants import CONFIG


class TocNode:
    def __init__(self, path, title, level):
        if not os.path.exists(path):
            raise UserError(f"'{path}' is not a file or directory.")
        self.path = path
        self.title = title
        self.level = level
        self.children = []

    def appendChild(self, child):
        path = os.path.join(self.path, child['path'])
        tocNode = TocNode(
            path, child['title'] if 'title' in child else child['path'], self.level + 1)
        if os.path.isdir(path):
            tocNode.processChildren(
                child['children'] if 'children' in child else [])
        self.children.append(tocNode)

    def processChildren(self, children):
        if not children:
            for subPath in os.listdir(self.path):
                self.appendChild({'path': subPath})
        else:
            for path in children:
                if path == '':
                    subPaths = os.listdir(self.path)
                    if 'order' in children[path]:
                        if children[path]['order'] == 'alphabetic':
                            subPaths.sort()
                        if children[path]['order'] == 'alphanumeric':
                            subPaths.sort(key=lambda item: (
                                int(item.partition(' ')[0]) if item[0].isdigit() else float('inf'), item))
                        elif children[path]['order'] == 'mtime':
                            subPaths.sort(key=lambda x: os.path.getmtime(
                                os.path.join(self.path, x)))
                        elif children[path]['order'] == 'ctime':
                            subPaths.sort(key=lambda x: os.path.getctime(
                                os.path.join(self.path, x)))
                        else:
                            raise UserError(
                                f"unknown order {children[path]['order']}")
                    for subPath in subPaths:
                        if subPath not in children:
                            self.appendChild({'path': subPath})
                else:
                    self.appendChild({**children[path], 'path': path})

    def toLinear(self):
        result = [self]
        for node in self.children:
            result += node.toLinear()
        return result

    @staticmethod
    def getNodes(config):
        root = TocNode(config.config[CONFIG.KEY.PROJECTS]
                       [CONFIG.KEY.PROJECT_DOC_HTML][CONFIG.KEY.SRC_DIR], 'root', 0)
        root.processChildren(
            config.config[CONFIG.KEY.PROJECTS][CONFIG.KEY.PROJECT_DOC_HTML][CONFIG.KEY.TOC])
        return root.toLinear()[1:]
