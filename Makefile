
help:
	@echo "\n----------========## Welcome to OPAL ##========----------"

	@echo "available commands:"
	@echo "   make setup"
	@echo "   make test"
	@echo "   make convert_c_to_ir"

test:
	@py.test --testdox --cov-branch --cov-report term-missing --cov-report=html --cov=opal --color=yes

setup:
	@pip install -r requirements-tests.txt

convert_c_to_ir:
	@find ./CLib -name "*.c" | xargs ./resources/c-to-llvm.sh
	@mv `find ./CLib -name "*.ll"` ./llvm_ir/
