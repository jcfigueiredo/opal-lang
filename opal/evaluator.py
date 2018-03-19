# noinspection PyPackageRequirements
from ctypes import CFUNCTYPE, c_void_p

# noinspection PyPackageRequirements
from llvmlite import binding as llvm

from opal.codegen import CodeGenerator, ASTVisitor
from opal.parser import parser


# noinspection PyMethodMayBeStatic


class OpalEvaluator:

    def __init__(self):
        self.codegen = CodeGenerator()

        # self.target = llvm.Target.from_triple("x86_64-apple-macosx10.12.0")

    def evaluate(self, code, print_ir=False):
        ast = ASTVisitor().transform(parser.parse(f'{code}'))

        self.codegen.generate_code(ast)

        module = self.codegen.module

        llvm_ir = str(module)

        llvm_mod = llvm.parse_assembly(llvm_ir)

        if print_ir:
            print(llvm_ir)

        llvm_mod.verify()

        target_machine = llvm.Target.from_default_triple().create_target_machine()
        with llvm.create_mcjit_compiler(llvm_mod, target_machine) as ee:
            ee.finalize_object()
            fptr = CFUNCTYPE(c_void_p)(ee.get_function_address('main'))

            fptr()
