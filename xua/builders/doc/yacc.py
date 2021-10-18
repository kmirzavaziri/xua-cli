from xua.helpers import Logger
import ply.yacc as yacc
from xua.builders.doc.lex import lexer, tokens

HEADING = 'heading'


def p_document(p):
    '''document : document element
                | element'''
    if len(p) == 3:
        p[0] = p[1].append(p[2])
    else:
        p[0] = [p[1]]


def p_element(p):
    '''element : command
               | heading
               | paragraph'''


def p_command(p):
    '''command : command PYTHON_COMMAND
               | PYTHON_COMMAND'''
    if len(p) == 3:
        p[0] = p[1].append(p[2])
    else:
        p[0] = [p[1]]


def p_heading(p):
    'heading : HEADING_INDICATOR text'
    p[0] = {
        'name': HEADING,
        'level': p[1],
        'content': p[2],
    }


def p_heading_spec_1(p):
    'heading : text NEW_LINE PLUS_2_EQUALS'
    p[0] = {
        'name': HEADING,
        'level': 1,
        'content': p[1],
    }


def p_heading_spec_2(p):
    '''heading : text NEW_LINE 2_DASHES
               | text NEW_LINE PLUS_3_DASHES'''
    p[0] = {
        'name': HEADING,
        'level': 2,
        'content': p[1],
    }


def p_paragraph(p):
    '''paragraph : paragraph text
                 | paragraph NEW_LINE text
                 | text'''


def p_text(p):
    '''text : text text_char
            | text_char'''
    if len(p) == 3:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]


def p_text_char(p):
    '''text_char : ESCAPED_CHAR
                 | CHAR'''
    p[0] = p[1]


def p_error(p):
    Logger.log(Logger.ERROR, '', 'Unexpected ' +
               p.type + ' at Line ' + str(p.lineno))


def parse(source):
    parser = yacc.yacc()
    return parser.parse(source, lexer=lexer)
