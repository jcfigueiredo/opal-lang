from opal.ast import ASTNode


class Continue(ASTNode):
    def dump(self):
        return 'Continue'
