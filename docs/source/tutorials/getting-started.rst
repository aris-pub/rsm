.. _getting-started:

Your First RSM Document
=======================

This tutorial takes you from zero to a rendered RSM manuscript. By the end you
will have installed RSM, written a short document, and previewed it in your
browser.

.. tip::

   If you want to skip installation and try RSM immediately, visit
   `RSM Studio <https://rsm.studio>`_ and start typing in the editor.


Step 1: Install RSM
--------------------

Install the ``rsm-lang`` package:

.. code-block:: bash

   $ pip install rsm-lang

Or with uv:

.. code-block:: bash

   $ uv add rsm-lang

Verify the installation:

.. code-block:: bash

   $ rsm --version

Step 2: Write a manuscript
--------------------------

Create a file called ``manuscript.rsm`` with the following contents:

.. rsm::
   :source-only:

   # My First Manuscript

   :author: {
     :name: Jane Scientist
     :affiliation: Example University
   } ::

   :abstract:
   A short demonstration of RSM markup.
   ::

   ## Introduction {:label: intro}

   RSM is a markup language for **web-first**
   scientific manuscripts.
   It supports *emphasis*, **bold text**,
   and $x^2 + y^2 = z^2$.

   ## Results

   We can reference the introduction
   using :ref:intro::.

Let's break down what's happening:

- ``#`` and ``##`` create headings (like Markdown)
- ``:author:``, ``:abstract:`` are **block tags** that introduce distinct parts of
  the manuscript
- ``:name:`` and ``:affiliation:`` are **meta tags** that add information to their
  parent tag
- ``**bold**`` and ``*italic*`` work like Markdown
- ``$...$`` renders inline mathematics
- ``:ref:intro::`` creates a cross-reference with an automatic tooltip
- ``::`` (the Halmos) closes any open tag


Step 3: Build and preview
-------------------------

Build the HTML output:

.. code-block:: bash

   $ rsm build manuscript.rsm

This creates ``manuscript.html`` and a ``static/`` folder. To preview with live
reload:

.. code-block:: bash

   $ rsm serve manuscript.rsm

Your browser will open automatically. Edit ``manuscript.rsm`` and save; the
browser refreshes on every change.


Step 4: Check with the linter
-----------------------------

RSM includes a linter that catches common issues:

.. code-block:: bash

   $ rsm check manuscript.rsm

Fix any warnings and rebuild.


What's next?
------------

- :ref:`markup`: deeper dive into RSM's tag system
- :ref:`handrail`: the interactive sidebar UI
- :ref:`guides`: task-oriented guides for styling, citations, and publishing
- :ref:`syntax`: complete syntax reference


Troubleshooting
---------------

Build errors
************

**"Command not found: rsm"**
   Make sure RSM is installed (``pip install rsm-lang``) and your virtual
   environment is activated.

**"Error: Could not find file manuscript.rsm"**
   Use ``cd`` to navigate to the directory containing your ``.rsm`` file, or
   provide the full path.

**"SyntaxError: unexpected tag at line X"**
   Run ``rsm check manuscript.rsm`` to see detailed error messages.
   Common causes: missing closing Halmos ``::``, misspelled tag name,
   or incorrect meta tag syntax (check braces and colons).

Linter warnings
***************

**"LINT: Manuscript with no title"**
   Add a title at the top of your file: ``# Your Title Here``

**"LINT: Missing closing Halmos"**
   Every opening tag needs a closing ``::``.
   Use proper indentation to track nested tags.

Browser issues
**************

**Manuscript doesn't render correctly**
   Try a hard refresh (``Ctrl+Shift+R`` or ``Cmd+Shift+R``).
   Check the browser console (F12) for JavaScript errors.
   Verify the ``static/`` folder is in the same directory as the HTML file.

**Math equations don't display**
   RSM uses Temml for math rendering. Try a hard refresh
   or use ``rsm serve`` for automatic rebuilds.

**Still stuck?**
   Open an issue at https://github.com/aris-pub/rsm/issues with your RSM
   version (``rsm --version``) and a minimal example.
