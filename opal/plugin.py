from collections import defaultdict


class Plugin(type):
    def __init__(cls, name, bases, nmspc):
        super(Plugin, cls).__init__(name, bases, nmspc)
        if not hasattr(cls, 'registry'):
            cls.registry = set()

        cls.registry.add(cls)
        cls.registry -= set(bases)  # Remove base classes

    __inheritors__ = defaultdict(list)

    def __new__(mcs, name, bases, dct):
        klass = type.__new__(mcs, name, bases, dct)
        for base in klass.mro()[1:-1]:
            mcs.__inheritors__[base].append(klass)
        return klass

    def __iter__(cls):
        return iter(cls.__inheritors__[cls])

    def by(cls, op):
        for klass in cls.registry:
            if klass.op == op:
                return klass

