.. _handrail:

The handrail
============

In the following example, hover (or tap, on mobile) on the manuscript title.

.. rsm::

   # Hover me!
   Introducing the handrail.

You will see a context menu appearing to the left of the manuscript title.  This area is
called the `handrail`.  It is an area that allows for interaction with individual parts
of the manuscript.  RSM markup automatically generates handrails for different parts of
the manuscript, such as sections and remarks.

.. rsm::

   # Handrails

   ## Sections have handrails

   :remark:
   Other special parts have
   handrails too, and so do paragraphs.
   ::

In general, any part of the manuscript that shows a gray border to the left admits
interaction via a handrail.

.. tip::

   If you are familiar with notebook interfaces such as Jupyter Notebooks, you may think
   of handrails in RSM as marking individual "cells" in a notebook.  The main difference
   is that in RSM, handrails may be nested within each other, while cells in a notebook
   are always consecutive.
