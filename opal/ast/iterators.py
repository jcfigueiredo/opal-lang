from opal.ast import ASTNode
from opal.ast.types import List, Integer


class IndexOf(ASTNode):

    def __init__(self, lst: List, index: Integer):
        self.lst = lst
        self.index = index

    def code(self, codegen):
        index = codegen.visit(self.index)
        vector = codegen.visit(self.lst)
        val = codegen.visit_vector(vector, index)
        return val

    def dump(self):
        return f'(position {self.index.val} {self.lst.dump()})'
