import operator

from rply import ParserGenerator

from opal.ast import Integer, Program, Div, Mul, Sub, Add, Block, Float

pg = ParserGenerator(
    ["INTEGER", "FLOAT", "MINUS", "PLUS", "DIV", "MUL", "$end", "NEWLINE"],
    precedence=[
        ("left", ["PLUS", "MINUS"]),
        ("left", ["MUL", "DIV"]),
    ])


@pg.production("main : program")
def main_program(state, p):
    return p[0]


@pg.production('program : block')
def program_statement(state, p):
    program = Program(block=p[0])
    return program


@pg.production('block : statement_full')
def block_expr(state, p):
    return Block(p[0])


@pg.production('block : statement_full block')
def block_expr_block(state, p):
    if type(p[1]) is Block:
        b = p[1]
    else:
        b = Block(p[1])

    b.add_statement(p[0])
    return b


@pg.production('statement_full : statement NEWLINE')
@pg.production('statement_full : statement $end')
def statement_full(state, p):
    return p[0]


@pg.production('statement : expression')
def statement_expr(state, p):
    return p[0]


# noinspection PyUnusedLocal
@pg.production("expression : expression PLUS expression")
@pg.production("expression : expression MINUS expression")
@pg.production("expression : expression DIV expression")
@pg.production("expression : expression MUL expression")
def expr_binop(state, p):
    op = p[1].getstr()
    ops = {
        "+": Add,
        "-": Sub,
        "*": Mul,
        "/": Div,  # floordiv because we support only integers for now
    }
    return ops[op](p[0], p[2])


# noinspection PyUnusedLocal
@pg.production("const : INTEGER")
def expr_integer(state, p):
    return Integer(int(p[0].getstr()))


@pg.production("const : FLOAT")
def expr_float(state, p):
    return Float(float(p[0].getstr()))


@pg.production('expression : const')
def expression_const(state, p):
    return p[0]


parser = pg.build()
