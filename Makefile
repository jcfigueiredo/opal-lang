
help:
	@echo "\n----------========## Welcome to OPAL ##========----------"

	@echo "available commands:"
	@echo "   make setup"
	@echo "   make test"
	@echo "   make convert_c_to_ir"

test:
	@py.test --testdox --cov-branch --cov-report term-missing --cov-report=html --cov=opal --cov-config .coveragerc --color=yes

setup:
	@pip install -r requirements-tests.txt

convert_c_to_ir:
	@for f in `find ./CLib -name "*.c"` ; do \
    	./resources/c-to-llvm.sh $$f ; \
    	echo "$$f converted"; \
	done
	@mv ./CLib/*.ll ./llvm_ir/
