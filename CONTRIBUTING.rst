Contributing to django-email-log
================================

Pull Requests
-------------

Feel free to open pull requests before you've finished your code or tests.
Opening your pull request soon will allow others to comment on it sooner.

A checklist of things to remember when making a feature:

- Write tests if applicable
- Note important changes in the `CHANGES`_ file
- Update the `README`_ file if needed
- Update the documentation if needed
- Add yourself to the `AUTHORS`_ file

.. _AUTHORS: AUTHORS.rst
.. _CHANGES: CHANGES.rst
.. _README: README.rst

Testing
-------

Please add tests for your pull requests and make sure your changes don't break
existing tests.  To run the tests against your code::

    python setup.py test

Please use tox to test the code against all supported versions of Python and
Django.  First install tox::

    pip install tox

To run tox and generate an HTML code coverage report (available in the
``htmlcov`` directory)::

    ./runtests.sh
