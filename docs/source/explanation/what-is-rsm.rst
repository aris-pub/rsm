.. _what-is-rsm:

What is RSM?
============

RSM (Readable Science Markup) is a markup language and toolchain for writing
**web-first scientific manuscripts**. Where LaTeX targets printed paper, RSM
targets pixels: responsive layout, interactive cross-references, and accessible
typography, out of the box.


The problem
-----------

Scientific publishing still assumes paper. LaTeX produces fixed-geometry PDFs
that don't adapt to screens, can't offer interactive navigation, and require
external tooling for web output. Markdown is too simple for structured academic
writing (no semantic tags, no first-class theorems, no cross-reference
tooltips). Quarto adds computational notebooks but inherits Pandoc's
limitations for formal mathematics.

RSM is purpose-built for researchers who want to publish on the web without
giving up the rigor of LaTeX.


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
   For any real number :math: x ::,
   :mathblock:
   e^{ix} = \cos x + i\sin x
   ::
   In particular, :math: e^{i\pi} + 1 = 0 ::.
   ::

   :proof:
   The proof follows from the Taylor series
   expansions of :math: e^x ::,
   :math: \cos x ::, and :math: \sin x ::.
   ::

   Setting :math: x = \pi :: in
   :ref:thm-euler:: yields the result.


What makes RSM different
------------------------

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


How it compares
---------------

.. list-table::
   :header-rows: 1
   :widths: 25 15 15 15 15

   * -
     - RSM
     - LaTeX
     - Markdown
     - Quarto
   * - **Output**
     - HTML
     - PDF
     - HTML (via converter)
     - HTML, PDF, etc.
   * - **Responsive**
     - Yes
     - No
     - Depends on theme
     - Yes
   * - **Structured proofs**
     - First-class
     - Via amsthm
     - No
     - Via LaTeX blocks
   * - **Interactive refs**
     - Automatic tooltips
     - No
     - No
     - Limited
   * - **Learning curve**
     - 1-2 hours
     - Weeks
     - 30 minutes
     - 2-3 hours

See :ref:`why-rsm` for detailed comparisons and design rationale.


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
