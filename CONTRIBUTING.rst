Contributing
============

Below is a list of tips for submitting issues and pull requests.  These are
suggestions and not requirements.


Submitting Issues
-----------------

Issues are often easier to reproduce/resolve when they have:

- A pull request with a failing test demonstrating the issue
- A code example that produces the issue consistently
- A traceback (when applicable)


How to submit changes
---------------------

Open a `pull request`_ to submit changes to this project.

Your pull request needs to meet the following guidelines for acceptance:

- The tox test suite must pass without errors and warnings.
- Include tests (if applicable). This project maintains 100% code coverage.
- Note important changes in the `CHANGES`_ file.
- Add documentation for new functionality.
- Update the `README`_ file if applicable.
- Add yourself to the `AUTHORS`_ file

Feel free to submit pull requests early as a work-in-progress: you can always iterate on the pull request after submission.

To run linting and code formatting checks before committing your change, you can install pre-commit as a Git hook by running the following command:

.. code:: console

    $ tox -e pre-commit install

It is recommended to open an issue before starting work on anything.
This will allow a chance to talk it over with the maintainers and validate your approach.

.. _pull request: https://github.com/treyhunner/django-email-log/pulls
.. _AUTHORS: AUTHORS.rst
.. _CHANGES: CHANGES.rst
.. _README: README.rst


Testing
-------

Please add tests for your code and ensure existing tests don't break.  To run
the tests against your code::

    python setup.py test

Please use tox to test the code against supported Python and Django versions.
First install tox::

    pip install tox

To run tox and generate a coverage report (in ``htmlcov`` directory)::

    ./runtests.sh

**Please note**: Before a pull request can be merged, all tests must pass and
code/branch coverage in tests must be 100%.
