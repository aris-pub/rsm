.. _handrail:

The Handrail
============

The handrail is RSM's interactive sidebar. It appears to the left of manuscript
elements when you hover over them, giving readers a way to navigate and interact
with the document's logical structure.


Seeing the handrail
*******************

Hover (or tap, on mobile) over the manuscript title below:

.. rsm::

   # Hover me!
   Introducing the handrail.

A context menu appears to the left. That area is the handrail.


What gets a handrail?
*********************

Sections, theorems, proofs, remarks, and paragraphs all have handrails. In
general, any part of the manuscript that shows a gray border on the left admits
interaction via a handrail.

.. rsm::

   # Handrails everywhere

   ## Sections have handrails

   :remark:
   Remarks have handrails too.
   ::

   :theorem:
   Theorems have handrails, and so do
   their proofs.
   ::

   :proof:
   Hover over this proof to see its
   handrail.
   ::

   And every paragraph has one as well.

Try hovering over each element to see its handrail appear.


Nested handrails
****************

Unlike cells in a notebook (which are always consecutive), handrails can be
nested. A theorem lives inside a section, and both have their own handrail.
Hovering over the inner element shows its handrail without hiding the outer one.

.. rsm::

   ## A section

   :definition:
   A **handrail** is an interactive region
   to the left of a manuscript element.
   ::

   Notice how the section and the definition
   each have their own handrail, and the
   definition's handrail is nested inside the
   section's.


The handrail menu
*****************

Each handrail has a small menu icon. Clicking it reveals options for that
element, such as copying a permalink or viewing the source markup. The exact
options depend on the type of element.

.. tip::

   If you are familiar with notebook interfaces such as Jupyter Notebooks, you
   may think of handrails as marking individual "cells". The key difference is
   that RSM handrails can be nested within each other, reflecting the document's
   logical structure.
