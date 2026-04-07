.. _converting-guide:

Converting Between RSM and Other Formats
========================================

RSM can import from and export to other document formats via Pandoc.

.. note::

   These commands require `Pandoc <https://pandoc.org/installing.html>`_
   to be installed.


Exporting RSM to LaTeX
----------------------

To export an RSM manuscript to LaTeX for journal submission:

.. code-block:: bash

   $ rsm export manuscript.rsm --to latex -o manuscript.tex

This produces a ``.tex`` file with a ``braiid.sty`` package in the same
directory. Compile with your usual LaTeX toolchain:

.. code-block:: bash

   $ pdflatex manuscript.tex


Exporting RSM to PDF
--------------------

To go directly to PDF (via Typst):

.. code-block:: bash

   $ rsm export manuscript.rsm --to pdf -o manuscript.pdf


Exporting to other formats
--------------------------

Any Pandoc-supported format works:

.. code-block:: bash

   $ rsm export manuscript.rsm --to docx -o manuscript.docx
   $ rsm export manuscript.rsm --to epub -o manuscript.epub


Importing a Markdown draft
--------------------------

To convert an existing Markdown file to RSM source:

.. code-block:: bash

   $ rsm import draft.md -o manuscript.rsm

The output is valid RSM that you can edit and build normally. You may need
to adjust the result for RSM-specific features like structured proofs or
``:config:`` settings.


Importing from LaTeX
--------------------

.. code-block:: bash

   $ rsm import paper.tex --from latex -o manuscript.rsm


Importing from other formats
-----------------------------

Specify the source format with ``--from``:

.. code-block:: bash

   $ rsm import document.docx --from docx -o manuscript.rsm
   $ rsm import page.html --from html -o manuscript.rsm


See also
--------

- :ref:`import-export-ref` for supported formats and limitations
- :ref:`cli-commands` for full command flag reference
