.. _cli-commands:

CLI Commands
============

RSM provides eight subcommands. Run ``rsm --help`` for a summary, or
``rsm <command> --help`` for details on any command.


rsm init
--------

Initialize a new RSM project in the current directory.

.. code-block:: bash

   $ rsm init
   $ rsm init --css         # also create a custom.css file
   $ rsm init --force       # overwrite existing files

**Flags:**

``--css``
   Create a ``custom.css`` file alongside the RSM source.

``--force``
   Initialize even if RSM files already exist in the directory.


rsm build
---------

Build an RSM source file to a complete HTML page with static assets.

.. code-block:: bash

   $ rsm build manuscript.rsm
   $ rsm build manuscript.rsm -o build/
   $ rsm build manuscript.rsm --standalone

Produces ``index.html`` (or the filename derived from the source) and a
``static/`` folder. This is the main command for producing output ready
to serve or publish.

**Flags (in addition to** :ref:`common flags <common-flags>` **):**

``--standalone``
   Output a single self-contained HTML file with inlined JS and CDN CSS.
   No ``static/`` folder is created.

``-o, --output PATH``
   Output path. Can be a directory or a filename.

``-p, --print``
   Print the generated HTML to stdout.

``--no-theme-toggle``
   Disable the dark mode toggle button.


rsm render
----------

Render RSM source to an HTML body fragment and print to stdout. No ``<head>``,
no static files. Useful for testing and piping.

.. code-block:: bash

   $ rsm render manuscript.rsm
   $ rsm render -c "## Hello\n\nWorld." -r

**Flags (in addition to** :ref:`common flags <common-flags>` **):**

``-s, --silent``
   Suppress HTML output, show only log messages.


rsm check
----------

Run the linter on an RSM source file. Reports warnings and suggestions
without producing any output.

.. code-block:: bash

   $ rsm check manuscript.rsm


rsm parse
----------

Parse RSM source and output the abstract syntax tree as JSON.

.. code-block:: bash

   $ rsm parse manuscript.rsm
   $ rsm parse manuscript.rsm --pretty

**Flags (in addition to** :ref:`common flags <common-flags>` **):**

``--pretty``
   Pretty-print JSON output with indentation.


rsm export
----------

Export RSM source to any Pandoc-supported format. Requires
`Pandoc <https://pandoc.org>`_.

.. code-block:: bash

   $ rsm export manuscript.rsm --to latex
   $ rsm export manuscript.rsm --to pdf -o manuscript.pdf

**Flags (in addition to** :ref:`common flags <common-flags>` **):**

``--to FORMAT``
   Output format (default: ``latex``). Any Pandoc-supported format:
   ``latex``, ``pdf``, ``docx``, ``epub``, ``typst``, etc.

``-o, --output PATH``
   Output file path. Omit to write to stdout.

See :ref:`import-export-ref` for format details and limitations.


rsm import
----------

Import a document in any Pandoc-supported format and convert it to RSM
source. Requires `Pandoc <https://pandoc.org>`_.

.. code-block:: bash

   $ rsm import draft.md -o manuscript.rsm
   $ rsm import paper.tex --from latex -o manuscript.rsm

**Flags:**

``--from FORMAT``
   Input format (default: ``markdown``). Any Pandoc-supported format.

``-c, --string``
   Interpret the source argument as a string, not a file path.

``-o, --output PATH``
   Output ``.rsm`` file path. Omit to write to stdout.

See :ref:`import-export-ref` for format details and limitations.


rsm serve
---------

Start a development server with live reload. Optionally builds an RSM file
first and rebuilds on changes.

.. code-block:: bash

   $ rsm serve manuscript.rsm
   $ rsm serve manuscript.rsm --port 8080
   $ rsm serve                  # serve current directory

**Flags:**

``--port PORT``
   Port number (default: 5500).

``--no-browser``
   Do not automatically open the browser.

``--standalone``
   Use standalone mode for builds.

``-o, --output PATH``
   Output path for builds.

``-p, --print``
   Print HTML to stdout on each rebuild.

``--no-theme-toggle``
   Disable dark mode toggle.

``--css PATH``
   Path to custom CSS file.

``--menu-right``
   Position handrail menus to the right.


.. _common-flags:

Common flags
------------

These flags are available on ``build``, ``render``, ``check``, ``parse``,
and ``export``:

``src``
   RSM source file path (positional argument).

``-c, --string``
   Interpret ``src`` as a source string instead of a file path.

``-r, --handrails``
   Include interactive handrails in output.

``--css PATH``
   Path to a custom CSS file.

``--menu-right``
   Position handrail context menus to the right instead of left.

``--strict``
   Halt on CST parse errors instead of continuing with warnings.

``-v, --verbose``
   Increase log verbosity. Use ``-vv`` for debug output.

``--log-no-timestamps``
   Exclude timestamps from log output.

``--log-no-lineno``
   Exclude line numbers from log output.

``--log-format {plain,rsm,json,lint}``
   Log output format (default: ``rsm``).


Notes
-----

1. ``rsm render`` uses the basic translator by default. Add ``-r`` to use
   the handrails translator (see :ref:`how-rsm-works`).
2. ``rsm check`` always uses ``lint`` log format regardless of ``--log-format``.
3. ``rsm build`` always enables handrails.
