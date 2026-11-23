.. _first-document:

Install RSM and write a first document
======================================

On this page you install RSM, write a short document and open it in your
browser. You need about ten minutes.

.. tip::

   To try RSM without installing anything, open `RSM Studio
   <https://rsm.studio>`_ and type in its editor.


Install RSM
-----------

RSM needs Python 3.11 or newer. Install the ``rsm-lang`` package:

.. code-block:: bash

   pip install rsm-lang

If you use uv, run ``uv tool install rsm-lang`` instead. Then check that the
``rsm`` command works:

.. code-block:: bash

   rsm --version


Write a document
----------------

Make a new folder, and in it a file called ``paper.rsm`` with this text:

.. rsm::

   # The Pythagorean Theorem

   :author: {
     :name: Ada Lovelace
     :affiliation: Analytical Engine Society
   } ::

   :abstract:
   We state the Pythagorean theorem and use it once.
   ::

   ## Statement

   In a right triangle with legs $a$ and $b$ and
   hypotenuse $c$, the lengths satisfy
   $a^2 + b^2 = c^2$.

   ## An example

   A triangle with legs 3 and 4 has a hypotenuse
   of length **5**, because $9 + 16 = 25$.

The part marked "Source" is the text that you write, and the part marked
"Result" is the page that RSM makes from it. Every example in these docs has
the same two parts.

The source uses four kinds of markup:

- ``#`` starts the title, and ``##`` starts a section. Sections get numbers.
- ``$...$`` holds math, written as LaTeX.
- ``**...**`` makes text bold, and ``*...*`` makes it italic.
- Words between colons, such as ``:author:`` and ``:abstract:``, are **tags**.
  A tag starts a part of the document, and ``::`` ends it.

Inside ``:author:``, the braces hold the tag's **meta keys**, here ``:name:``
and ``:affiliation:``. Meta keys add information to a tag. You will use tags
and meta keys on every page of the tutorial.


Build the page
--------------

In the folder that holds ``paper.rsm``, run:

.. code-block:: bash

   rsm build paper.rsm

RSM writes ``paper.html`` and a ``static/`` folder next to it. Open
``paper.html`` in a browser. The ``static/`` folder holds the page's fonts,
styles and scripts, so keep it next to the HTML file.


Preview while you write
-----------------------

``rsm serve`` builds the page, opens it in your browser and rebuilds it each
time you save the source:

.. code-block:: bash

   rsm serve paper.rsm

Change a sentence in ``paper.rsm``, save it, and the browser reloads with the
change. Stop the server with :kbd:`Ctrl-C`.


When something goes wrong
-------------------------

If a tag has no closing ``::``, or a tag name has a typo, RSM still builds the
page, but it prints a warning that gives the line and column of the problem:

.. code-block:: text

   WRN | The CST contains errors. | (12, 1) - (14, 3)

On the built page, the text at that place is marked in red. Fix the source and
build again.

``rsm check paper.rsm`` looks for the same problems without building, and also
gives style hints, each with its line and column:

.. code-block:: text

   src:5:6: WRN: The CST contains errors.
   src:3:1: LINT: Section with no label
