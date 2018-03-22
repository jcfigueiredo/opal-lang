# noinspection PyPackageRequirements
import glob
from ctypes import CFUNCTYPE, c_void_p

# noinspection PyPackageRequirements
from llvmlite import binding as llvm
from os import path

import opal
from opal.codegen import CodeGenerator, ASTVisitor
from opal.parser import parser


# noinspection PyMethodMayBeStatic


class OpalEvaluator:

    def __init__(self):
        self.codegen = CodeGenerator()
        self.llvm_mod = None

        # noinspection PyMethodMayBeStatic

    def _get_external_modules(self):

        clib_files_pattern = path.abspath(path.join(path.dirname(path.realpath(opal.__file__)), '../llvm_ir', '*.ll'))

        all_ir_files = glob.glob(clib_files_pattern)
        mods = []
        for file in all_ir_files:
            with open(file, 'r') as f:
                module_ref = llvm.parse_assembly(f.read())
                module_ref.verify()
                mods.append(module_ref)
        return mods

    def evaluate(self, code, print_ir=False):
        ast = ASTVisitor().transform(parser.parse(code))

        self.codegen.generate_code(ast)

        module = self.codegen.module

        llvm_ir = str(module)

        self.llvm_mod = llvm.parse_assembly(llvm_ir)

        external_modules = self._get_external_modules()
        for mod in external_modules:
            self.llvm_mod.link_in(mod)

        self.llvm_mod.verify()

        if print_ir:
            print(self.llvm_mod)

        target_machine = llvm.Target.from_default_triple().create_target_machine()

        with llvm.create_mcjit_compiler(self.llvm_mod, target_machine) as ee:

            ee.finalize_object()
            ee.run_static_constructors()
            fptr = CFUNCTYPE(c_void_p)(ee.get_function_address('main'))

            fptr()
