from opal.ast import Program, Add, Integer, Block, Mul, LogicError
from opal.lexer import pstate, lex
from opal.parser import parser


def parse(expr: str):
    return parser.parse(lex(expr), pstate)


class TestParsingExpressions:
    def test_returns_as_a_program(self):
        prog = parse("1 + 1")
        assert isinstance(prog, Program)

    def test_is_included_in_the_program(self):
        prog = parse("1 + 1")
        prog.block.statements.should.contain(Add(Integer(1), Integer(1)))


class TestDumpingExpressions:
    def test_works_for_programs(self):
        prog = parse("1 + 10")
        prog.dump().should.be.equal('(Program\n  (Block\n  (+ 1 10)))')

    def test_works_for_integer_consts(self):
        prog = parse("1")
        prog.dump().should.contain('(Block\n  (Integer 1))')

    def test_works_for_float_consts(self):
        prog = parse("1.0")
        prog.dump().should.contain('(Block\n  (Float 1.0))')

    def test_works_for_binops(self):
        prog = parse("1 + 2")
        prog.dump().should.contain('(+ 1 2)')

    def test_works_for_expressions(self):
        prog = parse("1 + 2 * 3")
        prog.dump().should.contain('(+ 1 (* 2 3))')

        prog = parse("10 / 2 * 3 - 1")
        prog.dump().should.contain('(- (* (/ 10 2) 3) 1)')

        prog = parse("10 * 2 / 3 - 1")
        prog.dump().should.contain('(- (/ (* 10 2) 3) 1)')

    def test_works_for_multi_line(self):
        prog = parse("1 * 2\n4 + 3\n2 - 1 + 4 * 2")
        prog.dump().should.contain('(* 1 2)\n(+ 4 3)\n(+ (- 2 1) (* 4 2))')


class TestComparingNodes:
    def test_works_for_programs(self):
        p1 = Program(
            Block(
                Add(Integer(8), Integer(10))
            )
        )
        p2 = Program(
            Block(
                Add(Integer(8), Integer(10))
            )
        )

        # noinspection PyUnresolvedReferences
        p1.should.be.equal(p2)


class TestABlock:
    def test_can_be_created_from_single_statement(self):
        body = Add(Integer(8), Integer(10))
        b1 = Block(
            body
        )
        b1.statements.should.contain(body)

    def test_can_be_created_from_a_list_of_statements(self):
        s1 = Add(Integer(8), Integer(10))
        s2 = Mul(Integer(18), Integer(1))
        body = [s1, s2, ]

        b1 = Block(body)
        b1.statements.should.contain(s1)
        b1.statements.should.contain(s2)

    def test_cant_be_created_with_empty_statement(self):
        b1 = Block()
        # noinspection PyStatementEffect
        b1.statements.should.be.empty


class TestValueNodes:
    def test_of_different_types_cant_be_compared(self):
        v1 = Integer(1)
        add = Add(Integer(81), Integer(14))

        expected_message = f'You can\'t compare a Value and {add.__class__.__name__}.' \
                           f'\nTokens being compared:\n{v1.dump()}\n{add}'

        # noinspection PyUnresolvedReferences
        v1.__eq__.when.called_with(add).should.throw(LogicError, expected_message)


class TestBinaryOperationNodes:
    def test_of_different_types_cant_be_compared(self):
        add = Add(Integer(18), Integer(120))
        v1 = Integer(1)

        expected_message = f'You can\'t compare a BinaryOp and {v1.__class__.__name__}.' \
                           f'\nTokens being compared:\n{add.dump()}\n{v1.dump}'

        # noinspection PyUnresolvedReferences
        add.__eq__.when.called_with(v1).should.throw(LogicError, expected_message)
