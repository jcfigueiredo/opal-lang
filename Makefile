
help:
	@echo "\n----------========## Welcome to OPAL ##========----------"

	@echo "available commands:"
	@echo "   make setup"
	@echo "   make test"
	@echo "   make convert_c_to_ir"

test: convert_c_to_ir
	@py.test --testdox --cov-branch --cov-report term-missing --cov-report=html --cov=opal --cov-config .coveragerc --color=yes
	@rm resources/coverage.svg
	@coverage-badge -o resources/coverage.svg

setup:
	@pip install -r requirements-tests.txt

convert_c_to_ir:
	@for f in `find ./CLib -name "*.c"` ; do \
    	./resources/c-to-llvm.sh $$f ; \
    	echo "$$f converted"; \
	done
	@mv ./CLib/*.ll ./llvm_ir/
