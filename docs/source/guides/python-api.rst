.. _guide-python-api:

Use RSM from Python
===================

The ``rsm`` package does from Python what the ``rsm`` command does from the
terminal: it turns RSM source into a web page, checks it, and converts it to
other formats. It also gives a program the parsed document as a tree of
Python objects. Install it with ``pip install rsm-lang``.

The examples on this page use this file, ``paper.rsm``:

.. code-block:: text

   # Odd and even

   ## Sums {:label: sec-sums}

   :theorem: {:label: thm-even, :title: Even sums}
   The sum of two even numbers is even.
   ::

   :lemma: {:label: lem-odd}
   The sum of two odd numbers is even.
   ::

   See :ref:thm-even::.


Turn RSM into HTML
------------------

``rsm.render`` returns the ``<body>`` of the page as a string, to put inside
a page of your own. Give it the source as a string, or the path of a file:

.. code-block:: python

   import rsm

   html = rsm.render(source="# Title\n\nSome *text*.\n")
   html = rsm.render(path="paper.rsm", handrails=True)

``handrails=True`` adds the controls that let the reader collapse blocks and
open their menus. ``render`` leaves them out by default.

``rsm.build`` returns a whole page, with its styles and scripts, as
``rsm build`` writes it:

.. code-block:: python

   page = rsm.build(path="paper.rsm")

   # One HTML file, with the styles and scripts inside it.
   page = rsm.build(path="paper.rsm", standalone=True)

   # Write paper.html and its static folder into site/.
   rsm.build(
       path="paper.rsm",
       write_output=True,
       output_dir="site",
       output_filename="paper.html",
   )


Read the structure of a document
--------------------------------

``ParserApp`` parses a document into a tree of nodes, one for each block and
each inline tag, with the numbers that RSM gives them. ``traverse`` walks the
tree and returns the nodes of one kind:

.. code-block:: python

   from rsm import nodes
   from rsm.app import ParserApp

   manuscript = ParserApp(srcpath="paper.rsm").run()
   for block in manuscript.traverse(nodeclass=nodes.Theorem):
       print(type(block).__name__, block.full_number, block.label, block.title)

This prints::

   Theorem 1.1 thm-even Even sums
   Lemma 1.2 lem-odd

A lemma is a kind of theorem in the tree, so ``nodeclass=nodes.Theorem``
finds both. See :ref:`python-api` for every node class, and
:ref:`how-rsm-works` for the steps between the source and the page.


Collect the warnings
--------------------

RSM logs its warnings, such as a reference to a label that does not exist,
with Python's ``logging`` module, under the name ``RSM``. To collect them,
add a handler to that logger:

.. code-block:: python

   import logging

   class Collect(logging.Handler):
       def __init__(self):
           super().__init__()
           self.messages = []

       def emit(self, record):
           self.messages.append(record.getMessage())

   collect = Collect()
   logging.getLogger("RSM").addHandler(collect)
   rsm.render(source="# T\n\nSee :ref:nope::.\n")
   print(collect.messages)  # ['Reference to nonexistent label "nope"']

To stop at the first syntax error instead of building around it, pass
``strict=True``. A source with an error then raises
``rsm.transformer.RSMTransformerError``, whose message lists each error with
its line and column:

.. code-block:: python

   rsm.build(source=text, strict=True)


Convert to and from other formats
---------------------------------

``pandoc_export`` and ``pandoc_import`` do what ``rsm export`` and
``rsm import`` do, and need Pandoc too. See :ref:`converting-guide`.

.. code-block:: python

   from rsm.app import pandoc_export, pandoc_import

   latex = pandoc_export(path="paper.rsm", to_format="latex")
   pandoc_export(path="paper.rsm", to_format="pdf", output="paper.pdf")

   source = pandoc_import(path="draft.md")
   source = pandoc_import(path="notes.docx", from_format="docx")

A format that is not text, such as PDF or Word, needs ``output``, the file to
write. For a text format, the result is returned as a string.
