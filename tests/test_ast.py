from llvmlite import ir

from opal.ast import Program, Add, Integer, Block, Mul, LogicError, Float, String, Print
from opal.codegen import ASTVisitor
from opal.parser import parser


def parse(expr):
    return ASTVisitor().transform(parser.parse(f'{expr}'))


class TestParsingExpressions:
    def test_returns_as_a_program(self):
        prog = parse("1 + 1")
        assert isinstance(prog, Program)

    def test_has_a_block(self):
        prog = parse("1 + 1")
        prog.block.should.equal(Block(Add(Integer(1), Integer(1))))

    def test_has_a_block_with_expression(self):
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

    def test_works_for_string_consts(self):
        prog = parse("'andrea'")
        prog.dump().should.contain('(Block\n  (String andrea))')

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
        prog = parse("1 * 2\n4 + 3\n2 - 1 + 4 * 2\n")
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


class TestIntegerNodes:
    def test_cast_to_int_when_initialized_with_strings(self):
        v1 = Integer('1')
        v1.val.should.be.a(int)

    def test_has_a_llvm_representation(self):
        Integer.as_llvm.should.be.equal(ir.IntType(32))

    def test_can_be_compared(self):
        Integer(1).should.be.equal(Integer(1))
        Integer(1).should_not.be.equal(Integer(2))


class TestFloatNodes:
    def test_cast_to_int_when_initialized_with_strings(self):
        v1 = Float('1.2')
        v1.val.should.be.a(float)

    def test_has_a_llvm_representation(self):
        Float.as_llvm.should.be.equal(ir.DoubleType())

    def test_can_be_compared(self):
        Float(10.135).should.be.equal(Float(10.135))
        Float(10.135).should_not.be.equal(Float(101.35))


class TestStringNodes:
    def test_cast_to_int_when_initialized_with_strings(self):
        v1 = String("oie")
        v1.val.should.be.a(str)

    def test_has_a_llvm_representation(self):
        String.as_llvm.should.be.equal(ir.IntType(8).as_pointer)


class TestPrintNodes:
    def test_can_be_compared(self):
        Print(Integer(10)).should.be.equal(Print(Integer(10)))
        Print(Integer(10)).should_not.be.equal(Print(Integer(11)))


class TestValueNodes:
    def test_of_different_types_cant_be_compared(self):
        v1 = Integer(1)
        add = Add(Integer(81), Integer(14))

        expected_message = f'You can\'t compare a Value and {add.__class__.__name__}.' \
                           f'\nTokens being compared:\n{v1.dump()}\n{add}'

        # noinspection PyUnresolvedReferences
        v1.__eq__.when.called_with(add).should.throw(LogicError, expected_message)

    def test_distinguish_by_type(self):
        Integer(1).should_not.be.equal(Float(1.0))
        Float(1.0).should_not.be.equal(Integer(1))


class TestBinaryOperationNodes:
    def test_of_different_types_cant_be_compared(self):
        add = Add(Integer(18), Integer(120))
        v1 = Integer(1)

        expected_message = f'You can\'t compare a BinaryOp and {v1.__class__.__name__}.' \
                           f'\nTokens being compared:\n{add.dump()}\n{v1.dump}'

        # noinspection PyUnresolvedReferences
        add.__eq__.when.called_with(v1).should.throw(LogicError, expected_message)
