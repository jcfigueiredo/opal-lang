import os

from lark.lark import Lark

import opal


class TestLarkParser:
    def get_parser(self):

        opal_path = os.path.dirname(opal.__file__)
        grammar_file_path =os.path.join(opal_path, 'grammars', 'opal.g')

        with open(grammar_file_path, 'r') as f:
            parser = Lark(f.read(), start='program', ambiguity='explicit')
        return parser

    def test_tree(self):
        expr = """
        (1 + 2) / 2.0 - 3 * 4
        """
        print(expr)
        res = self.get_parser().parse(expr)
        print(res.pretty())

        # from lark.tree import pydot__tree_to_png  # Just a neat utility function
        # pydot__tree_to_png(res, "opal-grammar.png")
