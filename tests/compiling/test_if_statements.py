from wurlitzer import pipes

from tests.helpers import get_representation, parse


class TestIfStatementsSyntax:
    def test_works_for_booleans_with_no_else(self):
        expr = """
        if true
            a = 1
        end
        print(a)
        """

        repres = get_representation(expr)
        repres.should.contain('if_ boolean true block ')
        repres.should.contain('assign name a int 1 ')
        repres.should.contain('print var a')

    def test_works_for_booleans_with_else(self):
        expr = """
        if true
            a = 1
        else
            a = 2
        end
        """

        repres = get_representation(expr)
        repres.should.contain('if_ boolean true')
        repres.should.contain('block assign name a int 1 ')
        repres.should.contain('block assign name a int 2')
        '''
        program block if_ boolean true 
            block assign name a int 1 
            block assign name a int 2 
        '''

    def test_works_for_multiline_else(self):
        expr = """
        if true
            a = 1
            b = 2.2
        else
            "amora"
            print(a)
        end

        1
        false
        """

        repres = get_representation(expr)
        repres.should.contain('if_ boolean true block')
        repres.should.contain('assign name a int 1 ')
        repres.should.contain('assign name b float 2.2')
        repres.should.contain('block string "amora"')
        repres.should.contain('print var a')

    def test_works_for_variable(self):
        expr = """
        green = true
        if green
            band = "day"
        end
        """

        repres = get_representation(expr)
        repres.should.contain('assign name green boolean true ')
        repres.should.contain('if_ var green block')
        repres.should.contain('assign name band string "day"')


class TestIfStatementsAST:
    def test_works(self):
        expr = """
        if true
            a = 10.5
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(Program\n  (Block\n  If((Boolean true)) Then((Block\n  (= a 10.5))))))')

    def test_works_for_if_then_else_conditionals(self):
        expr = """
        if false
            a = 'right'
        else
            b = 'wrong'
        end
        """
        prog = parse(expr)
        prog.dump().should.be.equal('(Program\n  (Block\n  If((Boolean false)) '
                                    'Then((Block\n  (= a "right")))) '
                                    'Else((Block\n  (= b "wrong")))))')

    def test_works_for_if_with_variables(self):
        expr = """

        if alpha
            beta = 'gamma'
        end
        """
        prog = parse(expr)
        prog.dump().should.be.equal('(Program\n  (Block\n  If((VarValue alpha)) Then((Block\n  (= beta "gamma"))))))')

    def test_works_for_if_with_consts(self):
        expr = """

        if 1
            beta = 'gamma'
        end
        """
        prog = parse(expr)
        prog.dump().should.be.equal('(Program\n  (Block\n  If((Integer 1)) Then((Block\n  (= beta "gamma"))))))')

    def test_works_for_if_with_expressions(self):
        expr = """

        if 1 + 3 * 4 - 5 + 2
            beta = 'gamma'
        end
        """
        prog = parse(expr)
        prog.dump().should.be.equal('(Program\n  (Block\n  If((+ (- (+ 1 (* 3 4)) 5) 2)) '
                                    'Then((Block\n  (= beta "gamma"))))))')

    def test_works_for_if_with_strings(self):
        expr = """

        if "pocoio"
            beta = 'gamma'
        end
        """
        prog = parse(expr)
        prog.dump().should.be.equal('(Program\n  (Block\n  If((String pocoio)) '
                                    'Then((Block\n  (= beta "gamma"))))))')


class TestIfStatements:
    def test_handles_then_branch(self, evaluator):
        message = """Goes in."""

        expr = f"""
        if true
            print("{message}")
        end
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain(message)

    def test_handles_else_branch(self, evaluator):
        message = """Goes out."""

        expr = f"""
        if false
            print("never gets here")
        else
            print("{message}")
        end
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain(message)

    def test_works_with_variables(self, evaluator):
        expr = f"""
        exists = true
        if exists
            print("oh yeah")
        else
            print("oh noh")
        end
        here = false
        if here
            print("it's here")
        else
            print("it's there")
        end
        """
        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('oh yeah')
        out.should.contain('it\'s there')

    def test_works_with_comparison(self, evaluator):
        expr = f"""
        if 10 < 20
            print("20!")
        end

        if 1 > 2
            print("you're crazy")
        else
            print("one's ok")
        end
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('20!')
        out.should.contain('one\'s ok')

    def test_can_be_nested(self, evaluator):
        expr = f"""
        a = true 
        b = true
        
        if a
            if b
                print("nested")
            end
        end
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('nested')

    def test_can_define_variables_inside_blocks(self, evaluator):
        expr = f"""
        a = true 
        
        if a
            b = true
            if b
                print("b in block")
            end
        end
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('b in block')

    def test_works_with_expressions(self, evaluator):
        expr = f"""
        if 1 + 2 * 3
            print("seven")            
        end

        if 1 - 1
            print("weird")
        else
            print("zero")
        end

        if 1.3 + 3.7
            print("5.0")
        end

        if 2 > 1
            print("2 gt 1")
        end
                
        if 3 < 4
            print("3 lt 4")
        end
        
        if 3 == 3
            print("3 eq 3")
        end

        if 4 != 4
            print("4 neq 4")
        else
            print("4 eq 4")
        end
        
        if 2 + 3 == 5
            print("2 + 3 == 5")
        end
                
        if (2 + 3) * 4 - 2 == 9 * 2
            print("eighteen")
        end
                
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('seven')
        out.should.contain('zero')
        out.should.contain('5.0')
        out.should.contain('2 gt 1')
        out.should.contain('3 lt 4')
        out.should.contain('3 eq 3')
        out.should.contain('4 eq 4')
        out.should.contain('2 + 3 == 5')
        out.should.contain('eighteen')
