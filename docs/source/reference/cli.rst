.. _ref-cli:

Command line
============

The ``rsm`` command builds, checks and converts RSM files. ``rsm --help``
lists the subcommands, and ``rsm <subcommand> --help`` lists the options of
one. ``rsm --version`` prints the version.

Each section below lists every option of its subcommand. Several
subcommands share these options:

``-c``, ``--string``
   Reads the source from the command line instead of a file, as in
   ``rsm render -c "# Title"``.

``-v``, ``--verbose``
   Prints more messages. Each ``-v`` adds a level, so ``-vv`` prints more
   than ``-v``.

``--log-format``
   The format of the messages: ``plain``, ``rsm``, ``json`` or ``lint``.
   The default is ``rsm``.

``--log-no-timestamps``
   Leaves the time out of the messages in the ``rsm`` and ``json`` formats.

``--log-no-lineno``
   Leaves the file name and line number of the RSM code that printed the
   message out of the messages in the ``rsm`` format, and the ``lineno``
   field out of the messages in the ``json`` format.

``--strict``
   Stops with an error at the first syntax error in the source.


.. _cli-build:

.. rst-class:: tag-card

Build ``rsm build``
-------------------

Builds a web page from an RSM file. By default it writes ``paper.html`` next
to ``paper.rsm``, and a ``static/`` folder with the fonts, styles and scripts.
The page has handrails.

.. rubric:: Syntax

.. code-block:: bash

   rsm build paper.rsm -o public/index

.. rubric:: Options

``-o``, ``--output``
   The path and name of the page, without ``.html``.

``--standalone``
   Writes one HTML file that holds everything, with no ``static/`` folder.

``--sidebar``
   Adds the reader sidebar, with the table of contents, the notation, the
   proof steps and the pinned blocks. See :ref:`reading-sidebar`.

``--css``
   A CSS file to add to the page. See :ref:`styling`.

``--menu-right``
   Opens the handrail menus on the right instead of the left.

``--no-theme-toggle``
   Leaves out the button that switches between light and dark mode.

``--strict``
   Stops with an error at the first syntax error, instead of building the
   page with the error marked.

It also takes ``-c``, ``-v``, ``--log-format``, ``--log-no-timestamps`` and
``--log-no-lineno``, described at the top of this page.

.. rubric:: Related

:ref:`Serve <cli-serve>`, :ref:`tutorial-build`.


.. _cli-serve:

.. rst-class:: tag-card

Serve ``rsm serve``
-------------------

Builds the page, opens it in the browser and builds it again each time the
file is saved. It takes every option of ``rsm build``, and these:

.. rubric:: Syntax

.. code-block:: bash

   rsm serve paper.rsm

.. rubric:: Options

``--port``
   The port of the local server. The default is 5500.

``--no-browser``
   Does not open the browser.

.. rubric:: Related

:ref:`Build <cli-build>`.


.. _cli-check:

.. rst-class:: tag-card

Check ``rsm check``
-------------------

Checks an RSM file for errors and prints each problem with its line and
column, without building a page.

.. rubric:: Syntax

.. code-block:: bash

   rsm check paper.rsm

.. rubric:: Options

``--log-format``
   The format of the messages: ``plain``, ``rsm``, ``json`` or ``lint``. The
   default for ``rsm check`` is ``lint``.

It also takes ``-c``, ``--log-no-timestamps`` and ``--log-no-lineno``,
described at the top of this page.

.. rubric:: Related

:ref:`Build <cli-build>`.


.. _cli-render:

.. rst-class:: tag-card

Render ``rsm render``
---------------------

Prints the HTML of the document body, with no page around it and no files.

.. rubric:: Syntax

.. code-block:: bash

   rsm render paper.rsm -r

.. rubric:: Options

``-r``, ``--handrails``
   Adds handrails. Without it, the HTML has none.

``-s``, ``--silent``
   Prints only the messages, not the HTML.

``--sidebar``
   Adds the reader sidebar. See :ref:`reading-sidebar`.

It also takes ``-c``, ``-v``, ``--log-format``, ``--log-no-timestamps``,
``--log-no-lineno`` and ``--strict``, described at the top of this page.

.. rubric:: Related

:ref:`Build <cli-build>`.


.. _cli-export:

.. rst-class:: tag-card

Export ``rsm export``
---------------------

Converts an RSM file to another format with `pandoc <https://pandoc.org>`_,
such as LaTeX, PDF, EPUB or Word. Pandoc must be installed. PDF export also
needs a LaTeX installation that includes ``xelatex``, such as TeX Live or MacTeX.

.. rubric:: Syntax

.. code-block:: bash

   rsm export paper.rsm --to latex -o paper.tex

.. rubric:: Options

``--to``
   The output format, such as ``latex``, ``pdf``, ``epub`` or ``docx``.

``-o``, ``--output``
   The output file. Without it, the result is printed. Export to PDF, Word
   (``docx``), OpenDocument (``odt``), EPUB and PowerPoint (``pptx``)
   requires this option, because these files are not text.

It also takes ``-c``, ``-v``, ``--log-format``, ``--log-no-timestamps``,
``--log-no-lineno`` and ``--strict``, described at the top of this page.

.. rubric:: Related

:ref:`Import <cli-import>`.


.. _cli-import:

.. rst-class:: tag-card

Import ``rsm import``
---------------------

Converts a file in another format to RSM with pandoc, such as Markdown,
LaTeX or Word. For LaTeX, the source can also be a folder or an archive that
holds a project of several files.

.. rubric:: Syntax

.. code-block:: bash

   rsm import paper.tex --from latex -o paper.rsm

.. rubric:: Options

``--from``
   The input format, such as ``markdown``, ``latex`` or ``docx``. The default
   is ``markdown``.

``--main``
   For a LaTeX project of several files, the main ``.tex`` file.

``-o``, ``--output``
   The output file. Without it, the result is printed.

It also takes ``-c``, ``-v``, ``--log-format``, ``--log-no-timestamps`` and
``--log-no-lineno``, described at the top of this page.

.. rubric:: Related

:ref:`Export <cli-export>`.


.. _cli-init:

.. rst-class:: tag-card

New project ``rsm init``
------------------------

Starts a project in the current folder. It asks for the file name and the
authors, and writes an ``.rsm`` file and an ``assets/`` folder.

.. rubric:: Syntax

.. code-block:: bash

   rsm init --css

.. rubric:: Options

``--css``
   Also writes a ``custom.css`` file.

``--force``
   Starts the project even if the folder already holds ``.rsm`` files.


.. _cli-parse:

.. rst-class:: tag-card

Parse ``rsm parse``
-------------------

Prints the parsed document as JSON, for tools that read RSM.

.. rubric:: Syntax

.. code-block:: bash

   rsm parse paper.rsm --pretty

.. rubric:: Options

``--pretty``
   Indents the JSON.

It also takes ``-c``, ``-v``, ``--log-format``, ``--log-no-timestamps``,
``--log-no-lineno`` and ``--strict``, described at the top of this page.
