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

RSM writes ``paper.tex`` and copies two things into the same folder:
``braiid.sty``, the LaTeX package that sets the look of the output, and a
``fonts`` folder with the fonts of the web page (Source Sans 3, Source Code
Pro and Montserrat). ``braiid.sty`` loads the fonts with ``fontspec``, so
compile with XeLaTeX or LuaLaTeX:

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

Pandoc makes the PDF with XeLaTeX, so this needs a LaTeX installation that
includes ``xelatex``, such as TeX Live or MacTeX. The PDF uses ``braiid.sty``
and the fonts that ship with RSM, so it looks the same as the LaTeX export,
on any computer.

For example, this document:

.. rsm::

   # Graphs without triangles

   :author: {
     :name: Ada Lovelace
     :affiliation: University of London
   } ::

   :abstract:
   We give a short proof of Mantel's theorem.
   ::

   ## Results

   :theorem: {:label: thm-mantel, :title: Mantel}
   A graph with $n$ vertices and no triangle has at most $n^2/4$ edges.
   ::

   :proof: {:of: thm-mantel}
   Let $e$ be the number of edges and $d(v)$ the degree of a vertex $v$. The
   two ends of an edge $uv$ have no common neighbor, so $d(u) + d(v) \le n$.
   Summing over the edges gives
   $$ {:label: eq-sum}
   \sum_{v} d(v)^2 = \sum_{uv} \big(d(u) + d(v)\big) \le n e.
   $$
   By the Cauchy-Schwarz inequality :cite:bondy::,
   $\sum_v d(v)^2 \ge (2e)^2/n$. With :ref:eq-sum::, this gives
   $4e^2/n \le ne$, that is, $e \le n^2/4$.
   ::

   :references:
   @book{bondy,
     author = {Bondy, J. A. and Murty, U. S. R.},
     title = {Graph Theory},
     year = {2008},
     publisher = {Springer}
   }
   ::

exports to this PDF (click the image to open the PDF):

.. image:: /_static/examples/mantel-pdf.png
   :target: ../_static/examples/mantel.pdf
   :alt: The first page of the PDF: the title, the author, the abstract,
         section 1 with Theorem 1.1 (Mantel), its proof with equation (1.1),
         and the references.
   :width: 600px


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

These formats have the same headings and numbers as the web page: "1
Results" for a section, "Theorem 1.1 (Mantel)." before a theorem, "Proof of
Theorem 1.1." before its proof, and "(1.1)" after a numbered equation.

When Pandoc cannot convert a formula to the target format, it writes the
formula as TeX, and RSM shows Pandoc's warning.


What an export leaves out
-------------------------

An exported file is static, so the parts of the page that the reader works
with are not in it: the handrails, the tooltips, the sidebar and the proof
tools.

A figure that holds HTML shows its ``:static:`` image. An ``:html:`` or
``:htmlblock:`` outside a figure is replaced by its ``:alt:`` text. If a figure
that holds HTML has no ``:static:``, or an ``:html:`` or ``:htmlblock:``
outside a figure has no ``:alt:``, the export stops with an error that gives
the line of each one. See :ref:`guide-interactive-figures`.


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
- sections as RSM sections, each with a label,
- the environments ``theorem``, ``lemma``, ``proposition``, ``corollary``,
  ``definition``, ``remark``, ``example``, ``exercise``, ``problem`` and
  ``porism`` as their RSM blocks, each with a label. A title, as in
  ``\begin{theorem}[Mantel]``, becomes the ``:title:``, and an environment
  declared with ``\newtheorem*`` gets ``:nonum:``,
- ``proof`` as ``:proof:``. A proof titled with a reference, as in
  ``\begin{proof}[Proof of Lemma~\ref{lem:key}]``, gets ``:of:`` with that
  lemma,
- display math as ``:mathblock:``. Math that LaTeX numbers, such as
  ``equation`` and ``align``, gets a label. Math that LaTeX leaves
  unnumbered, such as ``equation*`` and ``\[...\]``, gets ``:nonum:``.
  ``\tag`` is dropped, because RSM numbers the equations itself,
- ``\ref`` and ``\eqref`` as ``:ref:``. RSM writes the kind of the target in
  the text of a reference, so a word such as "Theorem" in
  ``Theorem~\ref{thm:main}`` is dropped,
- ``\cite`` as ``:cite:``, and the entries of the ``.bib`` file or of
  ``thebibliography`` as BibTeX entries in a ``:references:`` block.

Read the result before you build it. Pandoc does not read every LaTeX
package, RSM drops commands that it does not know, and an environment with
another name, such as ``thm`` from ``\newtheorem{thm}{Theorem}``, is imported
as plain text.


Import other formats
--------------------

Give the format to ``--from``, such as ``docx`` or ``html``:

.. code-block:: bash

   rsm import notes.docx --from docx -o notes.rsm

``--from`` takes any format that Pandoc can read.

See :ref:`ref-cli` for every option of ``rsm export`` and ``rsm import``.
