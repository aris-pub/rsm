.. _converting-guide:

Converting and exporting
========================

``rsm export`` turns an RSM document into LaTeX, PDF, Word and the other
formats that `Pandoc <https://pandoc.org>`_ can write. ``rsm import`` turns a
Markdown or LaTeX file, or a file in another format that Pandoc can read,
into RSM source. Both commands need Pandoc, which you install separately:
see https://pandoc.org/installing.html.


Export to LaTeX
---------------

.. code-block:: bash

   rsm export paper.rsm --to latex -o paper.tex

RSM writes ``paper.tex`` and copies ``braiid.sty``, the LaTeX package that
sets the look of the output, into the same folder. ``braiid.sty`` loads
``fontspec``, so compile with XeLaTeX or LuaLaTeX:

.. code-block:: bash

   xelatex paper.tex

The LaTeX keeps the structure of the document:

- Sections, theorems, proofs and equations have the same numbers as on the
  web page, so "Theorem 1.1" in the text and in the LaTeX are the same.
- Theorem-like blocks become LaTeX theorem environments, with their titles
  and their ``:blockname:``. A proof with ``:of:`` is titled "Proof of"
  followed by a link to the result.
- References and citations become links, and the ``:references:`` block
  becomes a numbered list of references.
- The title, the authors and the abstract go at the top.

Without ``-o``, the LaTeX is printed instead of written to a file.


Export to PDF
-------------

.. code-block:: bash

   rsm export paper.rsm --to pdf -o paper.pdf

Pandoc makes the PDF with LaTeX, so this needs a LaTeX installation that
includes ``pdflatex``, such as TeX Live or MacTeX. The PDF does not use
``braiid.sty``, so it has the default look of Pandoc's LaTeX output. The
numbers and the links are the same as in the LaTeX export.


Export to Word, EPUB and other formats
--------------------------------------

Give the format to ``--to``:

.. code-block:: bash

   rsm export paper.rsm --to docx -o paper.docx
   rsm export paper.rsm --to epub -o paper.epub
   rsm export paper.rsm --to markdown -o paper.md

``--to`` takes any format that Pandoc can write. Word (``docx``),
OpenDocument (``odt``), EPUB, PowerPoint (``pptx``) and PDF are not text,
so they need ``-o``. A text format such as Markdown is printed when ``-o`` is
left out.


What an export leaves out
-------------------------

An exported file is static, so the parts of the page that the reader works
with are not in it: the handrails, the tooltips, the sidebar and the proof
tools.

A figure that holds HTML shows its ``:static:`` image if it has one, and a
note that points to the web page otherwise. An ``:html:`` or ``:htmlblock:``
outside a figure is replaced by its ``:alt:`` text. See
:ref:`guide-interactive-figures`.


Import a Markdown file
----------------------

.. code-block:: bash

   rsm import draft.md -o paper.rsm

Markdown is the default input format. RSM writes:

- the ``title`` and ``author`` from the YAML block at the top of the file as
  the title and the ``:author:`` blocks,
- each heading as a section, one level below the title, so ``# Intro``
  becomes ``## Intro``,
- emphasis, lists, links, inline math and display math as the RSM
  equivalents.

Each section and each display equation gets a label, such as ``sec-1`` and
``eqn-1``, so that you can refer to it.

Without ``-o``, the RSM source is printed.


Import a LaTeX paper
--------------------

.. code-block:: bash

   rsm import paper.tex --from latex -o paper.rsm

The source can also be a folder that holds a LaTeX project of several files,
or an archive of one (``.zip``, ``.tar``, ``.tar.gz``). RSM finds the main
file, the one with ``\documentclass``, and puts in the files that it loads
with ``\input`` and ``\include``. When the project has several files with
``\documentclass``, RSM picks the one named ``main``, ``ms`` or ``paper``, or
you name it with ``--main``:

.. code-block:: bash

   rsm import project.zip --from latex --main paper.tex -o paper.rsm

RSM writes:

- ``\title``, ``\author`` and the ``abstract`` environment as the front
  matter,
- sections, theorems, proofs and equations as their RSM blocks, each with a
  label, and ``\ref`` and ``\eqref`` as ``:ref:``,
- ``\cite`` as ``:cite:``, and the entries of the ``.bib`` file or of
  ``thebibliography`` as BibTeX entries in a ``:references:`` block.

Read the result before you build it. Pandoc does not read every LaTeX
package, and RSM drops commands that it does not know.


Import other formats
--------------------

Give the format to ``--from``, such as ``docx`` or ``html``:

.. code-block:: bash

   rsm import notes.docx --from docx -o notes.rsm

``--from`` takes any format that Pandoc can read.

See :ref:`ref-cli` for every option of ``rsm export`` and ``rsm import``.
