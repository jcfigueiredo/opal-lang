help:
	@echo "Howdy?"
test:
	@py.test --testdox --cov-branch --cov-report term-missing --cov-report=html --cov=opal --color=yes
setup:
	@pip install -r requirements.txt 
	@pip install -r requirements-tests.txt
