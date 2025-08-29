all: init docs clean test

clean: _clean-build _clean-pyc
	rm -fr htmlcov/

_clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

_clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

_venv:
	if [[ ! -d .venv ]]; then python3 -m venv .venv; fi

_venv-build: _venv
	.venv/bin/python3 -m pip install .[build]

_venv-docs: _venv
	.venv/bin/python3 -m pip install .[docs]

_venv-test: _venv
	.venv/bin/python3 -m pip install .[test]

init: _venv-build _venv-test _venv-docs

test: _venv-test
	.venv/bin/python3 -m coverage erase
	.venv/bin/python3 -m tox
	.venv/bin/python3 -m coverage html

docs: _venv-build
	.venv/bin/sphinx-build -b html -d docs/_build/doctrees docs docs/_build/html

build: clean _venv-build
	.venv/bin/python3 -m build
	.venv/bin/python3 -m twine check dist/*

test-release:
	.venv/bin/python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

release: build
	.venv/bin/python3 -m twine upload dist/*
