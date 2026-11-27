.. _how-rsm-works:

How RSM works
=============

``rsm build paper.rsm`` turns the source into a page in a fixed order of
steps, and each step is a Python module (see :ref:`python-api`). This page
goes through the steps, then through what the scripts of the page do when a
reader opens it, and how export and import fit in. It is for programs that
use RSM from Python, and for anyone who wants to change RSM.


From source to page
-------------------

**Read** (:mod:`~rsm.reader`)
   The file is read into a string.

**Parse** (:mod:`~rsm.tsparser`)
   A parser made with `tree-sitter <https://tree-sitter.github.io/>`_, from
   the grammar in the ``tree-sitter-rsm`` repository, reads the string into a
   syntax tree that holds every tag, brace and ``::``. RSM then turns that
   tree into a tree of document parts, such as sections, theorems, steps and
   references, made of the classes in :mod:`~rsm.nodes`.

**Transform** (:mod:`~rsm.transformer`)
   A series of passes completes the tree. They collect the labels and link
   each reference, citation, footnote and aside to its target, number the
   sections and the numbered blocks, build the table of contents, and work
   out the steps of each proof: which earlier steps each step uses, and what
   is assumed and left to prove at each one (:mod:`~rsm.proof`).

**Check** (:mod:`~rsm.linter`)
   The linter looks for things that build but are likely mistakes, and
   gives warnings. ``rsm check`` stops after this step.

**Translate** (:mod:`~rsm.translator`)
   Each part of the tree becomes HTML, which makes the body of the page. The
   translator writes into the HTML what the scripts of the page need: the
   handrails, the numbers, the targets of the references, and, with
   ``--sidebar``, the sidebar with the graph of the steps of each proof.

**Build** (:mod:`~rsm.builder`)
   The body goes into a whole page, with the styles and scripts of RSM, and
   the images and other files of the document are gathered. With
   ``--standalone``, all of them go inside the page.

**Write** (:mod:`~rsm.writer`)
   The page is written to disk: ``paper.html`` with a ``static`` folder, or
   one HTML file with ``--standalone``.

``rsm render`` stops after the translate step and prints the body of the
page, and ``rsm.render`` does the same from Python.


When a reader opens the page
----------------------------

The page is complete as HTML: without JavaScript, it shows all of its text,
open. When the scripts run, they add the features of the page:

- MathJax typesets the math, and the page shows once the math and the fonts
  are in place, so that nothing moves after it shows,
- the handrails, the menus and the folding start to work, and the folds that
  the reader made on an earlier visit come back,
- the tooltips, the map of the document, the margin column and, on a page
  built with ``--sidebar``, the sidebar are set up,
- the reading settings that the reader chose on any RSM page of the same
  website are applied.

The scripts are files in ``rsm/static``, written as JavaScript modules. A
standalone page carries them as one bundle.


Export and import
-----------------

``rsm export`` uses the same read, parse and transform steps, then turns the
tree into the document format of `Pandoc <https://pandoc.org>`_, which writes
LaTeX, PDF, Word and the other formats. A filter (``braiid/braiid.lua``) and a
LaTeX package (``braiid/braiid.sty``) give the output the headings, numbers
and look of RSM. ``rsm import`` goes the other way: Pandoc reads the file,
and RSM writes RSM source from what Pandoc read. See :ref:`converting-guide`.
