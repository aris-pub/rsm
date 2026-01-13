.. _recipes:

Recipes
=======

Change font size
****************

There exist pre-determined types that can be added to any tag to change font size.

.. rsm::

   :rsm:

   :paragraph: {:types: tiny} Lorem ipsum.

   :paragraph: {:types: smallest} Lorem ipsum.

   :paragraph: {:types: smaller} Lorem ipsum.

   :paragraph: {:types: small} Lorem ipsum.

   :paragraph: {:types: normal} Lorem ipsum.

   :paragraph: {:types: large} Lorem ipsum.

   :paragraph: {:types: larger} Lorem ipsum.

   :paragraph: {:types: largest} Lorem ipsum.

   :paragraph: {:types: huge} Lorem ipsum.

   :paragraph: {:types: huger} Lorem ipsum.

   ::


These work on blocks, inlines, paragraphs, or even math blocks.

.. rsm::

   :rsm:

   $ {:types: tiny} 2 + 2 = 4$

   $ {:types: smallest} 2 + 2 = 4$

   $ {:types: smaller} 2 + 2 = 4$

   $ {:types: small} 2 + 2 = 4$

   $ {:types: normal} 2 + 2 = 4$

   $ {:types: large} 2 + 2 = 4$

   $ {:types: larger} 2 + 2 = 4$

   $ {:types: largest} 2 + 2 = 4$

   $ {:types: huge} 2 + 2 = 4$

   $ {:types: huger} 2 + 2 = 4$

   ::


Prevent automatic numbering
***************************

By default, all sections (and subsections) are numbered.  Prevent numbering of a section
by using ``:nonum:``.

.. rsm::

   :rsm:

   # First
   ::

   # Unnumbered
   :nonum:
   ::

   # Second
   ::

   ::

Other numbered blocks such as math blocks also accept ``:nonum:``.

.. rsm::

   :rsm:

   $$
   2 + 2 = 4
   $$

   $$
   :nonum:
   3 + 3 = 6
   $$

   $$
   4 + 4 = 8
   $$

   ::



LaTeX preamble
**************

In LaTeX, the preamble is a section of the document that contains, among other things,
definitions of commands that are local to the document.  This can be achieved in RSM by
defining new commands inside a hidden math block with no number.

.. rsm::

   :rsm:

   This is not valid math: $\tr(X)$.

   $$
   :types: hide
   :nonum:
     \DeclareMathOperator{\tr}{Tr}
   $$

   After the hidden block: $\tr(X)$.

   ::

By adding ``hide`` to ``:types:``, we tell RSM to not show the entire block.

Make sure to use ``:nonum:`` since otherwise the numbering of subsequent math blocks
will be shifted.

The LaTeX commands available to RSM are limited by MathJax.
