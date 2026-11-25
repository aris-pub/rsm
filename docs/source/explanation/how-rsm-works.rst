.. _how-rsm-works:

How RSM works
=============

``rsm build paper.rsm`` passes the source through six steps. Each step is a
Python module, listed under :ref:`reference`.


Read
----

The file is read into a string. Module: :mod:`~rsm.reader`.


Parse
-----

The parser turns the string into a tree, in two steps.

1. A parser made with `tree-sitter <https://tree-sitter.github.io/tree-sitter/>`_
   reads the source into a syntax tree that holds every tag, brace and
   ``::``. Editors use this tree for syntax colors, through the grammar's
   highlight query.
2. RSM turns the syntax tree into a tree of document parts, such as sections,
   theorems and references, made of the classes in :mod:`~rsm.nodes`.

Module: :mod:`~rsm.tsparser`.


Transform
---------

Several passes complete the tree. Among them:

- collect the labels, and link each reference and citation to its target,
- link footnotes and asides to their calls,
- number sections, theorems, equations, figures and tables,
- build the table of contents,
- work out the steps of each proof, which steps each step uses, and which
  assumptions hold at each step.

``rsm check`` stops after this step, and reports what it found. Modules:
:mod:`~rsm.transformer`, and ``rsm.proof`` for proofs.


Translate
---------

Each part of the tree becomes HTML, which makes the body of the page.
``rsm build`` adds handrails, and ``rsm render`` leaves them out unless it is
given ``-r``. Module: :mod:`~rsm.translator`.


Build
-----

The body goes into a full HTML page, with the styles and scripts, and the
images of the document are gathered. Module: :mod:`~rsm.builder`.


Write
-----

The page is written to disk, as ``paper.html`` next to a ``static/`` folder,
or as one file with ``--standalone``. Module: :mod:`~rsm.writer`.
