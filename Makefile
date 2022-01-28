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

init:
	pip install -U tox coverage Sphinx

test:
	coverage erase
	tox
	coverage html

docs: documentation

documentation:
	sphinx-build -b html -d docs/_build/doctrees docs docs/_build/html

dist: clean
	pip install -U wheel twine
	python setup.py sdist bdist_wheel
	twine check dist/*

test-release: dist
	pip install -U twine
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

release: dist
	pip install -U twine
	twine upload dist/*
