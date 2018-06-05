from operator import eq

from opal.ast import ASTNode
from opal.ast.terminals import Continue


class Program(ASTNode):

    def __init__(self, block=None):
        self.block = block and block or Block()

    def __eq__(self, o):
        return self.block.__eq__(o.block)

    def code(self, codegen):
        codegen.visit(self.block)
        codegen.branch(codegen.exit_blocks[0])
        codegen.position_at_end(codegen.exit_blocks[0])
        codegen.builder.ret_void()

    def dump(self):
        s = f"({self.__class__.__name__}\n  {self.block.dump()})"
        return s


class Block(ASTNode):

    def __init__(self, body=None):
        if isinstance(body, list):
            self._statements = body
            return

        self._statements = []
        if body:
            self._statements.append(body)

    def __eq__(self, o):
        return any(map(eq, self.statements, o.statements))

    @property
    def statements(self):
        return self._statements

    def code(self, codegen):
        ret = None
        for stmt in self._statements:
            # TODO: This won't work but keeping this for now
            if isinstance(stmt, Continue):
                return
            temp = codegen.visit(stmt)
            if temp:
                ret = temp
        return ret

    def dump(self):
        stmts = '\n'.join([stmt.dump() for stmt in self._statements])

        s = f"({self.__class__.__name__}\n  {stmts})"
        return s
