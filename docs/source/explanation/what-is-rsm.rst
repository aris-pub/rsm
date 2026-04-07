.. _what-is-rsm:

What is RSM?
============

RSM (Readable Science Markup) is a markup language and toolchain for writing
**web-first scientific manuscripts**. Where LaTeX targets printed paper, RSM
targets pixels: responsive layout, interactive cross-references, and accessible
typography, out of the box.


A minimal example
-----------------

.. rsm::

   # Euler's Identity

   :author: {
     :name: Leonhard Euler
     :affiliation: Berlin Academy
   } ::

   :abstract:
   A brief note on a remarkable equation.
   ::

   ## The identity

   :theorem: {
     :label: thm-euler
   }
   For any real number $x$,
   $$
   e^{ix} = \cos x + i\sin x
   $$
   In particular, $e^{i\pi} + 1 = 0$.
   ::

   :proof:
   The proof follows from the Taylor series
   expansions of $e^x$,
   $\cos x$, and $\sin x$.
   ::

   Setting $x = \pi$ in
   :ref:thm-euler:: yields the result.


What you get
------------

**Semantic tags, not presentational commands.**
Every RSM tag (``:theorem:``, ``:proof:``, ``:cite:``, ``:ref:``) carries
meaning, not just formatting. The toolchain uses this structure to generate
tooltips, navigation, and accessibility features automatically.

**Interactive by default.**
Cross-references show tooltip previews on hover. The handrail sidebar lets
readers navigate the logical structure of the document. No JavaScript plugins
to configure.

**Responsive and accessible.**
RSM output adapts to any screen size. Readers can change fonts, enable dark
mode, and use screen readers. The CSS-based layout engine handles this
natively, with no fixed page geometry.

**Structured proofs.**
RSM has first-class support for theorem environments, proof steps, sub-proofs,
and sketches, not as macros but as language-level constructs with
cross-referencing built in.

For detailed comparisons with LaTeX, Markdown, and Quarto, see :ref:`why-rsm`.


Try it now
----------

**No installation required**: visit `RSM Studio <https://rsm.studio>`_ and
start typing.

**Local install**:

.. code-block:: bash

   pip install rsm-lang
   rsm build manuscript.rsm

**Learn more**: :ref:`getting-started` walks you from zero to rendered output
in 10 minutes.
