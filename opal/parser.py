import os

from lark import Lark

import opal


def _get_grammar():
    opal_path = os.path.dirname(opal.__file__)
    grammar_file_path = os.path.join(opal_path, 'grammars', 'opal.g')

    with open(grammar_file_path, 'r') as f:
        grammar = f.read()
    return grammar


def get_parser():
    return Lark(_get_grammar(), start='program', ambiguity='resolve', lexer='auto', parser='earley')


parser = get_parser()
