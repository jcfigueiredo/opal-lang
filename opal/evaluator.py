from llvmlite import binding as llvm

from opal.codegen import LLVMCodeGenerator
from opal.lexer import lex, pstate
from opal.parser import parser


class OpalEvaluator:

    def __init__(self):
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        self.codegen = LLVMCodeGenerator()

        self.target = llvm.Target.from_default_triple()

    def execute(self, code):
        ast = parser.parse(lex(code), pstate)
        self.codegen.generate_code(ast)

        mod_ir = str(self.codegen.module)
        mod_ir = mod_ir.replace("unknown-unknown-unknown", "x86_64-apple-macosx10.12.0")

        return mod_ir
