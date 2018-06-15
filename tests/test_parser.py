from opal.ast.visitor import ASTVisitor
from opal.ast.binop import Mul, Div, Add, Sub
from opal.ast.statements import Print
from opal.ast.types import Integer, Float, String
from opal.parser import parser


def parse(expr, only_statements=True):
    """
    Process some src code and returns the first statement of the Program
    :param only_statements: Bool.
    :param expr: src code
    :return: Integer ast Node
    """
    program = ASTVisitor().transform(parser.parse(f'{expr}'))
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
        parse("1 - 1\n2 * 3\n", only_statements=False).block.statements.should.be.equal(
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

    def test_supports_strings(self):
        parse("'alpha' + 'beta'").should.contain(
            Add(String('alpha'), String('beta'))
        )


class TestPrint:
    def test_strings(self):
        string = "howdy ho"
        parse(f'print(\'{string}\')').should.contain(Print(String(string)))

    def test_int(self):
        integer = 42
        parse(f'print({integer})').should.contain(Print(Integer(integer)))

    def test_float(self):
        float_ = 0.42
        parse(f'print({float_})').should.contain(Print(Float(float_)))

    def test_expr(self):
        parse(f'print(2 / 3 - 1)').should.contain(Print(Sub(Div(Integer(2), Integer(3)), Integer(1))))

    def test_expr_with_parenthesis(self):
        parse(f'print(2 / (3 - 1))').should.contain(Print(Div(Integer(2), Sub(Integer(3), Integer(1)))))

