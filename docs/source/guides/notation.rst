.. _guide-notation:

Notation
========

Authors in different fields use different symbols for the same thing. For
example, an eigenvalue is :math:`\lambda` in one book and :math:`\mu` in
another. In RSM, you declare the
symbols of a document once, with the form that you prefer, and the reader can
change how each one is shown. Every equation of the page follows the change.

This page builds one short document with its own notation. The tag is listed
in :ref:`Notation <tag-notation>`.


The whole document
------------------

.. rsm::
   :sidebar:

   # Symmetric matrices

   :notation:
     \eig $\lambda$ eigenvalue
     \inner $\langle #1, #2 \rangle$ inner product
   ::

   ## Results

   :theorem: {:label: thm-real, :title: Every $\eig$ is real}
   Let $A$ be a real symmetric matrix. Every eigenvalue $\eig$ of $A$ is real.
   ::

   :proof:
   Let $Ax = \eig x$ with $x \neq 0$. Then
   $$
   \eig \inner{x}{x} = \inner{Ax}{x} = \inner{x}{Ax} = \bar{\eig} \inner{x}{x},
   $$
   and $\inner{x}{x} > 0$, so $\eig = \bar{\eig}$.
   ::

The rest of this page goes through the parts of this document.


Declare a symbol
----------------

Put a ``:notation:`` block near the top of the document, after the title.
Each line declares one symbol, with three parts:

- the LaTeX command that you write in the math, such as ``\eig``,
- the form that the page shows by default, as math between ``$``, such as
  ``$\lambda$``,
- a name for the symbol, such as ``eigenvalue``. The sidebar lists the
  symbols by this name.

The block shows nothing in the page.


Use a symbol
------------

Write the command in any math of the document, inline or displayed, and in
the titles of blocks, as in the title of the theorem above. Use the command
every time that you mean the symbol, so that every use follows when the
reader changes it.


Symbols with arguments
----------------------

A symbol can take arguments, written ``#1``, ``#2`` and so on in its default
form, as in LaTeX. The inner product above takes two:

.. rsm::
   :source-only:

   \inner $\langle #1, #2 \rangle$ inner product

and ``\inner{Ax}{x}`` in the math shows :math:`\langle Ax, x \rangle`.


Commands that the reader cannot change
--------------------------------------

For a LaTeX command that is a shortcut and not a symbol, such as ``\R`` for
:math:`\mathbb{R}`, use ``\newcommand`` in a displayed equation with
``:preamble:`` instead. See :ref:`Displayed math <tag-mathblock>`.


What the reader can do
----------------------

With ``rsm build --sidebar``, the sidebar has a "Notation" view, with one row
for each symbol:

- The reader types new LaTeX for the symbol, such as ``\mu``, and clicks
  "Rename". Every use of the symbol in the page changes. LaTeX that does not
  build is refused.
- A button scrolls to the nearest use of the symbol.
- A button returns the symbol to the form that the author chose.

The page keeps the reader's choices when it is opened again in the same
browser, and "Copy link" in the sidebar copies them into the link.

The example at the top of this page is built with the sidebar. Choose "Wide"
above its page, open "Notation" from the strip of icons on the left, and
change :math:`\lambda` to :math:`\mu`.
