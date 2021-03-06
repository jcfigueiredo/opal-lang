import os

from lark import Lark

import opal


def _get_grammar():
    opal_path = os.path.dirname(opal.__file__)
    grammar_file_path = os.path.join(opal_path, 'grammars', 'opal.g')

    with open(grammar_file_path, 'r') as f:
        grammar = f.read()
    return grammar


class Parser:

    def __init__(self):
        self.lark = Lark(_get_grammar(), start="program", lexer="standard")

    def parse(self, string):
        return self.lark.parse(f'{string}\n')


def get_parser():
    return Parser()


parser = get_parser()
