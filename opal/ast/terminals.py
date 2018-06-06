from opal.ast import ASTNode


class Continue(ASTNode):
    def dump(self):
        return 'Continue'


class Break(ASTNode):
    # noinspection PyMethodMayBeStatic
    def code(self, codegen):
        codegen.is_break = True
        return codegen.branch(codegen.loop_end_blocks[-1])

    def dump(self):
        return 'Break'


class Return(ASTNode):
    def __init__(self, val):
        self.val = val

    def code(self, codegen):
        previous_block = codegen.builder.block
        codegen.position_at_end(codegen.exit_blocks[-1])
        ret = codegen.builder.ret(codegen.visit(self.val))
        codegen.position_at_end(previous_block)
        return ret

    def dump(self):
        return f'(Return {self.val.dump()})'
