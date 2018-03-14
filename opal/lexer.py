import re

from rply import LexerGenerator

lg = LexerGenerator()
lg.add('FLOAT', '-?\d+\.\d+')
lg.add('INTEGER', r'-?\d+')
lg.add("PLUS", r"\+")
lg.add("MINUS", r"\-")
lg.add("MUL", r"\*")
lg.add("DIV", r"/")
lg.add('NEWLINE', '\n')  # always last

# ignore whitespace
lg.ignore('[ \t\r\f\v]+')

lexer = lg.build()


# state instance which gets passed to parser
class ParserState(object):
    def __init__(self):
        # we want to hold a dict of declared variables
        self.variables = {}


# noinspection SpellCheckingInspection
pstate = ParserState()


def lex(source):
    multiline = r'([\s]+)(?:\n)'

    line = re.search(multiline, source)
    while line is not None:
        start, end = line.span(1)
        assert start >= 0 and end >= 0
        source = source[0:start] + source[end:]  # remove string part that was an empty line
        line = re.search(multiline, source)

    # print "source is now: %s" % source

    return lexer.lex(source)
