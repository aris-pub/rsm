.. _contributing:

Contributing
============

RSM is developed in the open, in the `aris-pub/rsm
<https://github.com/aris-pub/rsm>`_ repository on GitHub.


Ask a question
--------------

Search the `discussions <https://github.com/aris-pub/rsm/discussions>`_ for a
similar question first. If there is none, `start a discussion
<https://github.com/aris-pub/rsm/discussions/new>`_.


Ask for a feature
-----------------

`Start a discussion <https://github.com/aris-pub/rsm/discussions/new>`_ that
says what you want to do and why.


Report a bug
------------

`Open an issue <https://github.com/aris-pub/rsm/issues/new>`_ with:

- the shortest RSM source that shows the bug,
- what you expected, and what happened,
- the version of RSM (``rsm --version``), and the browser if the bug is on
  the page.

If you are not sure that it is a bug, start a discussion instead.


Change the code or the docs
---------------------------

You need Python 3.11 or newer, `uv <https://docs.astral.sh/uv/>`_ and
`just <https://just.systems>`_. Clone the repository with its submodule,
which holds the grammar, and install:

.. code-block:: bash

   git clone --recurse-submodules https://github.com/aris-pub/rsm.git
   cd rsm
   just install

Then:

- ``just test-fast`` runs the fast tests. To run the tests for what you
  changed, give pytest their files, such as
  ``uv run pytest tests/test_pandoc.py``. The tests of the page in a browser
  are in ``tests/interactive``, and need ``uv run playwright install
  chromium`` once.
- ``just lint`` formats the code and fixes what the linter can, and
  ``just typecheck`` checks the types.
- ``just docs`` builds these docs into ``docs/build``, and ``just
  docs-serve`` serves them and rebuilds them on every change.
- After a change to the grammar in ``tree-sitter-rsm``, ``just grammar``
  rebuilds it. After a change to the scripts in ``rsm/static``, ``just
  js-bundle`` rebuilds the bundle that standalone pages use.

Send the change as a pull request. The checks on GitHub run the tests,
including the screenshot tests. Those compare the page with images made on
GitHub, so they fail on most other computers and are checked only there. :ref:`how-rsm-works` explains the steps
from source to page and the module that makes each one, and
``CONTRIBUTING.md`` in the repository has the rules for code and tests.
