from opal.ast import ASTNode
from opal.ast.types import Bool


class If(ASTNode):

    def __init__(self, cond, then_, else_=None):
        self.cond = cond
        self.then_ = then_
        self.else_ = else_

    def dump(self):
        else_ = self.else_ and f' Else({self.else_.dump()})' or ''
        s = f'If({self.cond.dump()}) Then({self.then_.dump()})){else_}'
        return s

    def code(self, codegen):

        start_block = codegen.add_block('if.start')
        codegen.branch(start_block)
        codegen.position_at_end(start_block)

        if_true_block = codegen.add_block('if.true')
        end_block = codegen.add_block('if.end')

        cond = codegen.visit(self.cond)

        if cond.type != Bool.as_llvm():
            cond = codegen.cast(cond, Bool)

        if_false_block = end_block

        if self.else_:
            if_false_block = codegen.add_block('if.false')

        codegen.cbranch(cond, if_true_block, if_false_block)

        codegen.position_at_end(if_true_block)

        codegen.visit(self.then_)

        codegen.branch(end_block)

        if self.else_:
            codegen.position_at_end(if_false_block)
            codegen.visit(self.else_)
            codegen.branch(end_block)

        codegen.position_at_end(end_block)
