.. _cross-references-guide:

Cross-referencing Theorems and Equations
========================================

This guide covers labeling tags and referencing them throughout your
manuscript.


Labeling a tag
--------------

Any block-level tag can be given a label using the ``:label:`` meta tag:

.. rsm::

   :theorem: {
     :label: main-thm
   }
   Every RSM tag can be labeled
   and referenced.
   ::


Referencing by label
--------------------

Use ``:ref:<label>::`` to create a cross-reference. The rendered link includes an
automatic tooltip showing the referenced content:

.. rsm::

   :theorem: {
     :label: thm-example
   }
   This is our main result.
   ::

   As shown in :ref:thm-example::, the
   result follows.


Custom display text
-------------------

Override the default reference text in two ways.

**At the definition** (affects all references): use ``:reftext:``:

.. rsm::

   :theorem: {
     :label: thm-a
     :reftext: Main Theorem
   }
   A theorem with custom reftext.
   ::

   See :ref:thm-a::.

**At the reference** (affects one reference): use ``:ref:<label>, <text>::``:

.. rsm::

   :lemma: {
     :label: lem-b
   }
   A useful lemma.
   ::

   By :ref:lem-b, our key lemma::, the
   proof is complete.


Referencing equations
---------------------

Math blocks can be labeled and referenced the same way:

.. rsm::

   :mathblock: {
     :label: eqn-euler
   }
   e^{i\pi} + 1 = 0
   ::

   Equation :ref:eqn-euler:: is known as
   Euler's identity.


.. admonition:: Summary

   Use ``:label:`` to name any tag. Use ``:ref:<label>::`` to link to it.
   Customize display text with ``:reftext:`` (global) or
   ``:ref:<label>, text::`` (local). All references display with tooltips.
