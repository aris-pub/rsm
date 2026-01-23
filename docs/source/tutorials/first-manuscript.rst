.. _first-manuscript:

Your first manuscript
=====================

Create a new file called :code:`manuscript.rsm` and add the following contents

.. code-block:: text

   ## Introduction
   Web-first scientific publishing.

In the command line, :code:`cd` to the directory where the :code:`manuscript.rsm` file
is stored and execute

.. code-block:: bash

   $ rsm build manuscript.rsm

This will create a new file called :code:`manuscript.html` in the same directory. Use
:code:`rsm serve` to open this file with your web browser to see the output created by
RSM.

RSM provides a linter as a command line utility.  Run the following command to see what
the linter suggests.

.. code-block:: bash

   $ rsm check manuscript.rsm
   src:1:12: LINT: Manuscript with no title

Here, the linter is telling us that our manuscript is missing a title.  We can rectify
that by editing :code:`manuscript.rsm` as follows

.. code-block:: text

   # Readable Science Markup

   ## Introduction
   Web-first scientific publishing.

Run again the ``rsm check`` command, and the warning should have disappeared. You can
now run ``rsm build`` again and refresh your browser to see now the title of your
manuscript displayed.

.. tip::

   ``rsm serve`` will automatically rebuild the html file and refresh your browser when
   it detects changes in the source file.


Troubleshooting
===============

Common issues when getting started with RSM:

Build errors
************

**"Command not found: rsm"**

- Solution: Make sure RSM is installed: ``pip install rsm-lang``
- Check installation: ``rsm --version``
- If using a virtual environment, ensure it's activated

**"Error: Could not find file manuscript.rsm"**

- Solution: Use ``cd`` to navigate to the directory containing your ``.rsm`` file
- Or provide the full path: ``rsm build /path/to/manuscript.rsm``

**"SyntaxError: unexpected tag at line X"**

- Solution: Run ``rsm check manuscript.rsm`` to see detailed error messages
- Common causes:
  - Missing closing Halmos ``::``
  - Misspelled tag name (e.g. ``:section`` instead of ``:section:``)
  - Incorrect meta tag syntax (check braces and colons)

Linter warnings
***************

**"LINT: Manuscript with no title"**

- Not an error, but good practice to add a title
- Add at the top of your file: ``# Your Title Here``

**"LINT: Missing closing Halmos"**

- Every opening tag needs a closing ``::``
- Example: ``:section: content ::`` not ``:section: content``
- Use proper indentation to track nested tags

Browser issues
**************

**"Manuscript doesn't render correctly in browser"**

- Try a hard refresh: ``Ctrl+Shift+R`` (Linux/Windows) or ``Cmd+Shift+R`` (Mac)
- Check browser console (F12) for JavaScript errors
- Verify ``static/`` folder is in same directory as ``index.html``

**"Math equations don't display"**

- RSM uses MathJax for math rendering (loads from CDN)
- Check your internet connection
- Or serve locally: ``rsm build manuscript.rsm --serve`` (includes local MathJax)

Still stuck?
************

- Check existing GitHub issues: https://github.com/aris-pub/rsm/issues
- Open a new issue with:
  - Your RSM version (``rsm --version``)
  - Minimal example that reproduces the problem
  - Full error message
