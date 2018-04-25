import re

from opal.parser import get_parser


def get_representation(expr):
    # noinspection PyShadowingNames
    def parsed_representation(prog):
        repres = prog.pretty()
        repres = re.sub(r"\s+", ' ', repres)
        return repres[:-1]

    prog = get_parser().parse(f'{expr}')
    repres = parsed_representation(prog)
    return repres
