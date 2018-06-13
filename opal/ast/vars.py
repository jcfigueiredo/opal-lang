from opal.ast import Value


class Var(Value):
    def __init__(self, val):
        self.val = val

    # TODO: review this to codegen instead of returning an ASTNode
    # noinspection PyUnusedLocal
    def code(self, codegen):
        return self


class VarValue(Value):
    def __init__(self, val):
        self.val = val

    def code(self, codegen):
        name = codegen.symtab[self.val]
        return codegen.load(name)
