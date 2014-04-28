

upload: test register
	python setup.py sdist upload

register:
	python setup.py register

################################################################################


test: check
	RESOURCES_DIR=$(RESOURCES_DIR) python -m unittest discover -p '*_test.py'

reinstall: uninstall install

install:check
	python setup.py install

uninstall:
	pip uninstall --yes proso-geography-analysis

check:
	pep8 --exclude=migrations --ignore=E501,E225,E123,E128 proso
	pep8 --exclude=migrations --ignore=E501,E225,E123,E128 scripts
	pyflakes proso

