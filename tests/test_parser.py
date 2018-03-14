from opal.ast import Integer, Add, Sub, Mul, Div
from opal.lexer import lexer, pstate, lex
from opal.parser import parser


def parse(expr, only_statements=True):
    """
    Process some src code and returns the first statement of the Program
    :param expr: src code
    :return: Integer ast Node
    """
    program = parser.parse(lex(expr), pstate)
    if only_statements:
        return program.block.statements
    return program


class TestProgram:
    def test_has_a_block(self):
        parse("1 + 1", only_statements=False).should.have.property('block')

    def test_block_has_statements(self):
        parse("1 + 1", only_statements=False). \
            block.should.have.property('statements').which.should.be.a(list)

    def test_supports_multiple_lines(self):
        parse("1 - 1\n2 * 3", only_statements=False).block.statements.should.be.equal(
            [
                Sub(Integer(1), Integer(1)),
                Mul(Integer(2), Integer(3)),
            ]
        )


class TestOperationsIncludes:
    def test_addition(self):
        parse("1 + 1").should.contain(Add(Integer(1), Integer(1)))

    def test_subtraction(self):
        parse("6 - 2").should.contain(Sub(Integer(6), Integer(2)))

    def test_multiplication(self):
        parse("7 * 2").should.contain(Mul(Integer(7), Integer(2)))

    def test_division(self):
        parse("14 / 2").should.contain(Div(Integer(14), Integer(2)))

    def test_division_floors_down(self):
        parse("15 / 2").should.contain(Div(Integer(15), Integer(2)))


class TestTheParser:
    def test_supports_negative_numbers(self):
        parse("1 + -1").should.contain(Sub(Integer(1), Integer(-1)))

    def test_respects_precedences(self):
        parse("1 + 2 * 3").should.contain(
            Add(Integer(1), Mul(Integer(2), Integer(3)))
        )

        parse("2 / 3 - 1").should.contain(
            Sub(Div(Integer(2), Integer(3)), Integer(1))
        )

        parse("5 * 2 - 3").should.contain(
            Sub(Mul(Integer(5), Integer(2)), Integer(3))
        )
