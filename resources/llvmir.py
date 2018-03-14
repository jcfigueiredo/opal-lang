import llvmlite.ir as ll
import llvmlite.binding as llvm

llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()  # yes, even this one

module = ll.Module()

mainfn_type = ll.FunctionType(ll.IntType(64), [])

func = ll.Function(module, mainfn_type, name='main')

bb_entry = func.append_basic_block('entry')

builder = ll.IRBuilder()
builder.position_at_end(bb_entry)
# builder.ret(mulinstr)

ll.Constant(ll.IntType(64), 190)

stackint = builder.alloca(ll.IntType(64), name='myint')
builder.store(ll.Constant(stackint.type.pointee, 123), stackint)
myint = builder.load(stackint, 'myint')
builder.ret(myint)

# -------------------------------------------------------------------------------------------------------------------------
# fntype = ll.FunctionType(ll.IntType(32), [ll.IntType(32), ll.IntType(32)])
#
# module = ll.Module()
#
# func = ll.Function(module, fntype, name='foo')
# bb_entry = func.append_basic_block()
#
# builder = ll.IRBuilder()
# builder.position_at_end(bb_entry)
#
# stackint = builder.alloca(ll.IntType(32))
# builder.store(ll.Constant(stackint.type.pointee, 123), stackint)
# myint = builder.load(stackint)
#
# addinstr = builder.add(func.args[0], func.args[1])
# mulinstr = builder.mul(addinstr, ll.Constant(ll.IntType(32), 123))
# pred = builder.icmp_signed('<', addinstr, mulinstr)
# builder.ret(mulinstr)
#
# bb_block = func.append_basic_block()
# builder.position_at_end(bb_block)
#
# bb_exit = func.append_basic_block()
#
# pred = builder.trunc(addinstr, ll.IntType(1))
# builder.cbranch(pred, bb_block, bb_exit)
#
# builder.position_at_end(bb_exit)
# builder.ret(myint)

def create_execution_engine():
    """
    Create an ExecutionEngine suitable for JIT code generation on
    the host CPU.  The engine is reusable for an arbitrary number of
    modules.
    """
    # Create a target machine representing the host
    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    # And an execution engine with an empty backing module
    backing_mod = llvm.parse_assembly("")
    engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
    return engine


def compile_ir(engine, llvm_ir):
    """
    Compile the LLVM IR string with the given engine.
    The compiled module object is returned.
    """
    # Create a LLVM module object from the IR
    mod = llvm.parse_assembly(llvm_ir)
    mod.verify()
    # Now add the module and make sure it is ready for execution
    engine.add_module(mod)
    engine.finalize_object()
    return mod


execution_engine = create_execution_engine()

llvm_ir = str(module)
# print(llvm_ir)
print(compile_ir(execution_engine, llvm_ir))
