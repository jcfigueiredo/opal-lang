from opal.ast import ASTNode
from opal.ast.types import List, Integer


class IndexOf(ASTNode):

    def __init__(self, lst: List, index: Integer):
        self.lst = lst
        self.index = index

    def code(self, codegen):
        index = codegen.visit(self.index)
        vector = codegen.visit(self.lst)
        val = codegen.vector_get(vector, index)
        return val

    def dump(self):
        return f'(position {self.index.val} {self.lst.dump()})'


class While(ASTNode):

    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def code(self, codegen):
        cond_block = codegen.add_block('while.cond')
        body_block = codegen.add_block('while.body')

        codegen.loop_cond_blocks.append(cond_block)
        end_block = codegen.add_block('while.end')
        codegen.loop_end_blocks.append(end_block)

        codegen.branch(cond_block)
        codegen.position_at_end(cond_block)

        cond = codegen.visit(self.cond)
        codegen.cbranch(cond, body_block, end_block)
        codegen.position_at_end(body_block)

        codegen.visit(self.body)

        if not codegen.is_break:
            codegen.branch(cond_block)
        else:
            codegen.is_break = False

        codegen.position_at_end(end_block)
        codegen.loop_end_blocks.pop()
        codegen.loop_cond_blocks.pop()

    def dump(self):
        return f'While({self.cond.dump()}) {self.body.dump()}'


class For(ASTNode):

    def __init__(self, var, iterable, body):
        self.var = var
        self.iterable = iterable
        self.body = body

    def dump(self):
        return f'For({self.var.dump()} in {self.iterable.dump()}) {self.body.dump()}'

    def code(self, codegen):
        init_block = codegen.add_block('for.init')
        cond_block = codegen.add_block('for.cond')
        codegen.loop_cond_blocks.append(cond_block)

        body_block = codegen.add_block('for.body')
        end_block = codegen.add_block('for.end')
        codegen.loop_end_blocks.append(end_block)

        codegen.branch(init_block)
        codegen.position_at_end(init_block)
        vector = codegen.visit(self.iterable)

        size = codegen.call('vector_size', [vector])

        size = codegen.alloc_and_store(size, Integer.as_llvm(), name='size')
        index = codegen.alloc_and_store(codegen.const(0), Integer.as_llvm(), 'index')

        codegen.branch(cond_block)
        codegen.position_at_end(cond_block)

        should_go_on = codegen.builder.icmp_signed('<', codegen.load(index), codegen.load(size))

        codegen.cbranch(should_go_on, body_block, end_block)

        codegen.position_at_end(body_block)

        pos = codegen.load(index)
        val = codegen.vector_get(vector, pos)

        codegen.assign(self.var.val, val, Integer.as_llvm())

        codegen.visit(self.body)

        if not codegen.is_break:
            codegen.builder.store(codegen.builder.add(codegen.const(1), pos), index)
            codegen.branch(cond_block)
        else:
            codegen.is_break = False

        codegen.position_at_end(end_block)
        codegen.loop_end_blocks.pop()
        codegen.loop_cond_blocks.pop()