from _ast import If

from rply import LexerGenerator, ParserGenerator
from rply.token import BaseBox


class LogicError(Exception):
    pass


class Variable(BaseBox):
    def init(self, name):
        self.name = str(name)
        self.value = None

    def getname(self):
        return str(self.name)

    def eval(self, env):
        if env.variables.get(self.name, None) is not None:
            self.value = env.variables[self.name].eval(env)
            return self.value
        raise LogicError("Not yet defined")

    def to_string(self):
        return str(self.name)


class Boolean(BaseBox):
    def init(self, value):
        self.value = bool(value)

    def eval(self, env):
        return self

    def to_string(self):
        return str(self.value).lower()


lg = LexerGenerator()

# build up a set of token names and regexes they match
lg.add('FLOAT', '-?\d+.\d+')
lg.add('INTEGER', '-?\d+')
lg.add('STRING', '(""".?""")|(".?")|(\'.?\')')
lg.add('BOOLEAN', "true(?!\w)|false(?!\w)")
lg.add('IF', 'if(?!\w)')
lg.add('ELSE', 'else(?!\w)')
lg.add('END', 'end(?!\w)')
lg.add('AND', "and(?!\w)")
lg.add('OR', "or(?!\w)")
lg.add('NOT', "not(?!\w)")
lg.add('LET', 'let(?!\w)')
lg.add('FUNCTION', 'func(?!\w)')
lg.add('MODULE', 'mod(?!\w)')
lg.add('IMPORT', 'import(?!\w)')
lg.add('IDENTIFIER', "[a-zA-Z_][a-zA-Z0-9_]?")
lg.add('==', '==')
lg.add('!=', '!=')
lg.add('>=', '>=')
lg.add('<=', '<=')
lg.add('>', '>')
lg.add('<', '<')
lg.add('=', '=')
lg.add('[', '\[')
lg.add(']', ']')
lg.add('{', '{')
lg.add('}', '}')
lg.add('|', '\|')
lg.add(',', ',')
lg.add('DOT', '\.')
lg.add('COLON', ':')
lg.add('PLUS', '\+')
lg.add('MINUS', '\-')
lg.add('MUL', '\*')
lg.add('DIV', '/')
lg.add('MOD', '%')
lg.add('(', '\(')
lg.add(')', '\)')
lg.add('NEWLINE', '\n')

# ignore whitespace
lg.ignore('[ \t\r\f\v]+')

lexer = lg.build()

pg = ParserGenerator(
    # A list of all token names, accepted by the parser.
    ['STRING', 'INTEGER', 'FLOAT', 'IDENTIFIER', 'BOOLEAN',
     'PLUS', 'MINUS', 'MUL', 'DIV',
     'IF', 'ELSE', 'COLON', 'END', 'AND', 'OR', 'NOT', 'LET', 'WHILE',
     '(', ')', '=', '==', '!=', '>=', '<=', '<', '>', '[', ']', ',',
     '{', '}',
     '$end', 'NEWLINE', 'FUNCTION',

     ],
    # A list of precedence rules with ascending precedence, to
    # disambiguate ambiguous production rules.
    precedence=[
        ('left', ['FUNCTION', ]),
        ('left', ['LET', ]),
        ('left', ['=']),
        ('left', ['[', ']', ',']),
        ('left', ['IF', 'COLON', 'ELSE', 'END', 'NEWLINE', 'WHILE', ]),
        ('left', ['AND', 'OR', ]),
        ('left', ['NOT', ]),
        ('left', ['==', '!=', '>=', '>', '<', '<=', ]),
        ('left', ['PLUS', 'MINUS', ]),
        ('left', ['MUL', 'DIV', ]),
    ]
)


@pg.production('statement : expression')
def statement_expr(state, p):
    return p[0]


class Assignment(object):

    def __init__(self, identifier, value):
        pass


@pg.production('statement : LET IDENTIFIER = expression')
def statement_assignment(state, p):
    return Assignment(Variable(p[1].getstr()), p[3])


@pg.production('expression : IF expression COLON statement END')
def expression_if_single_line(state, p):
    return If(condition=p[1], body=p[3])


tokens = lexer.lex("let a = if true: 1 end")

# import ipdb; ipdb.set_trace()
t = tokens.next()
while t:
    print(t)
    try:
        t = tokens.next()
    except StopIteration as ex:
        break
