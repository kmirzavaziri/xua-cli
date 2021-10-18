import re
import ply.lex as lex
from xua.helpers import Logger

tokens = (
    'ESCAPED_CHAR', 'NEW_LINE', 'PYTHON_COMMAND',
    'CONTEXT', 'OPEN', 'OPEN_QUOTE', 'CLOSE', 'CLOSE_QUOTE',
    'PLUS_2_SPACES_END', 'WHITE_SPACES',
    'HEADING_INDICATOR',
    'PLUS_2_EQUALS', 'SIGN_EQUAL',
    'PLUS_3_DASHES', '2_DASHES', 'SIGN_DASH',
    'PLUS_3_ASTERISK', 'SIGN_ASTERISK',
    'PLUS_3_UNDERSCORE', 'SIGN_UNDERSCORE',
    'LIST_NUM',
    'SIGN_PLUS',
    'TRIPLE_BACKTICK', 'DOUBLE_BACKTICK', 'SINGLE_BACKTICK',
    'SIGN_OPEN_BRACKET', 'SIGN_CLOSE_BRACKET', 'SIGN_OPEN_PARENTHESIS', 'SIGN_CLOSE_PARENTHESIS',
    'SIGN_DOUBLE_QUOTATION', 'SIGN_SINGLE_QUOTATION',
    'SIGN_LESS', 'SIGN_GREATER',
    'SIGN_EXCLAMATION',
    'SIGN_PIPE', 'SIGN_COLON',
    'CHAR',
)


def t_ESCAPED_CHAR(t):
    r"""\\(\r\n|\r|\n|%|\\|`|\*|_|\{|\}|\[|\]|<|>|\(|\)|\#|\+|\-|\.|\!|\||"|'|)"""
    t.value = t.value[1:]
    if t.value in ['\r\n', '\r', '\n']:
        t.lexer.lineno += 1
    return t


def t_NEW_LINE(t):
    r'(\r\n|\r|\n)([\ \t]*$)?'
    t.lexer.lineno += 1
    return t


def t_comment(t):
    r'%.*$'
    return None


def t_PYTHON_COMMAND(t):
    r'@python\ .*'
    t.value = t.value[t.value.find('@python ') + len('@python '):]
    return t


def t_CONTEXT(t):
    r'^(\ {, 3}[>\t])?(>|\ {4}|\t)+'
    if t.value.startswith(' ' * 3) and t.value[3] != ' ':
        t.value = t.value[3:]
    t.value = t.value.replace(' ' * 4, '\t')
    return t


def t_PLUS_2_SPACES_END(t):
    r'\ {2,}$'
    return t


def t_WHITE_SPACES(t):
    r'[^\S\r\n]+'


def t_HEADING_INDICATOR(t):
    r'\#+'
    t.value = t.value.count('#')
    return t


def t_PLUS_2_EQUALS(t):
    r'={2,}'
    return t


def t_SIGN_EQUAL(t):
    r'='
    return t


def t_PLUS_3_DASHES(t):
    r'-{3,}'
    return t


def t_2_DASHES(t):
    r'-{2,}'
    return t


def t_SIGN_DASH(t):
    r'-'
    return t


def t_PLUS_3_ASTERISK(t):
    r'\*{3,}'
    return t


def t_SIGN_ASTERISK(t):
    r'\*'
    return t


def t_PLUS_3_UNDERSCORE(t):
    r'_{3,}'
    return t


def t_SIGN_UNDERSCORE(t):
    r'_'
    return t


def t_LIST_NUM(t):
    r'\d+\.'
    return t


def t_SIGN_PLUS(t):
    r'\+'
    return t


def t_TRIPLE_BACKTICK(t):
    r'```'
    return t


def t_DOUBLE_BACKTICK(t):
    r'``'
    return t


def t_SINGLE_BACKTICK(t):
    r'`'
    return t


def t_SIGN_OPEN_BRACKET(t):
    r'\['
    return t


def t_SIGN_CLOSE_BRACKET(t):
    r'\]'
    return t


def t_SIGN_OPEN_PARENTHESIS(t):
    r'\('
    return t


def t_SIGN_CLOSE_PARENTHESIS(t):
    r'\)'
    return t


def t_SIGN_DOUBLE_QUOTATION(t):
    r'"'
    return t


def t_SIGN_SINGLE_QUOTATION(t):
    r"'"
    return t


def t_SIGN_LESS(t):
    r'<'
    return t


def t_SIGN_GREATER(t):
    r'>'
    return t


def t_SIGN_EXCLAMATION(t):
    r'!'
    return t


def t_SIGN_PIPE(t):
    r'\|'
    return t


def t_SIGN_COLON(t):
    r':'
    return t


def t_CHAR(t):
    r'.'
    return t


def t_error(t):
    Logger.log(Logger.ERROR, '', f"Illegal character '{t.value[0]}'.")
    t.lexer.skip(1)


############################################
# Handle Indentation and Quote Blocks ######
############################################


def _new_token(type, lineno):
    token = lex.LexToken()
    token.type = type
    token.value = None
    token.lineno = lineno
    return token


def filter(lexer, add_endmarker=True):
    context = []

    class Object:
        pass
    doc = Object()
    doc.renderComments = 'none'
    doc.renderCodes = 'none'
    doc.constants = Object()

    tokens = iter(lexer.token, None)
    token = None
    for token in tokens:
        if token.type == "PYTHON_COMMAND":
            exec(token.value)
        else:
            if doc.renderComments == 'doc':
                if token.type == 'CONTEXT':
                    commonPrefixLen = 0
                    while commonPrefixLen < len(context) and commonPrefixLen < len(token.value) and context[commonPrefixLen] == token.value[commonPrefixLen]:
                        commonPrefixLen += 1
                    for s in reversed(context[commonPrefixLen:]):
                        yield _new_token('CLOSE_QUOTE', token.lineno) if s == '>' else _new_token('CLOSE', token.lineno)
                    for s in token.value[commonPrefixLen:]:
                        yield _new_token('OPEN_QUOTE', token.lineno) if s == '>' else _new_token('OPEN', token.lineno)
                else:
                    yield token

    if add_endmarker:
        yield _new_token('ENDMARKER', token.lineno if token is not None else 1)


class xLexer(object):

    def __init__(self, debug=0, optimize=0, lextab='lextab', reflags=0):
        self.lexer = lex.lex(debug=debug, optimize=optimize,
                             lextab=lextab, reflags=reflags)
        self.tokens = None

    def input(self, s, add_endmarker=True):
        self.lexer.input(s)
        self.tokens = filter(self.lexer, add_endmarker)

    def token(self):
        try:
            return next(self.tokens)
        except StopIteration:
            return None


lexer = xLexer(reflags=re.MULTILINE | re.VERBOSE)
