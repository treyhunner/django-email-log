all: init docs clean test

clean: clean-build clean-pyc
	rm -fr htmlcov/

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

venv:
	if [[ ! -d .venv ]]; then python3 -m venv .venv; fi

venv-build: venv
	.venv/bin/python3 -m pip install .[build]

venv-docs: venv
	.venv/bin/python3 -m pip install .[docs]

venv-test: venv
	.venv/bin/python3 -m pip install .[test]

init: venv-build venv-test

test: venv-test
	.venv/bin/python3 -m coverage erase
	.venv/bin/python3 -m tox
	.venv/bin/python3 -m coverage html

docs: documentation

documentation: venv-build
	.venv/bin/sphinx-build -b html -d docs/_build/doctrees docs docs/_build/html

build: dist

dist: clean venv-build
	.venv/bin/python3 -m build
	.venv/bin/python3 -m twine check dist/*

test-release:
	.venv/bin/python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

release: dist
	.venv/bin/python3 -m twine upload dist/*
