.. _import-export-ref:

Import and Export
=================

RSM can convert to and from other document formats using
`Pandoc <https://pandoc.org>`_ as an intermediary.

.. note::

   Pandoc must be installed separately. See https://pandoc.org/installing.html.


Export (RSM to other formats)
-----------------------------

``rsm export`` converts an RSM manuscript to any Pandoc-supported output format.

**Supported output formats**: ``latex``, ``pdf``, ``docx``, ``epub``,
``markdown``, ``html``, ``rst``, and any other format Pandoc supports.

**Pipeline**: RSM source → RSM AST → Pandoc JSON AST → target format.

For LaTeX and PDF output, RSM uses a Lua filter (``braiid.lua``) that maps
theorem-like blocks and proofs to LaTeX environments. Theorem-like blocks and
display equations print the numbers that RSM gives them, so their numbers agree with
the text of references to them, and a block's ``:blockname:`` names it in its
heading. LaTeX output also uses a custom ``braiid.sty`` package for its look.

For PDF output, Pandoc makes the PDF with LaTeX. This needs a LaTeX
installation that includes ``pdflatex``, and an output file given with ``-o``.
The PDF uses the default look of Pandoc's LaTeX output, not the BRAIID style.

**Limitations**:

- Interactive features (handrails, tooltips) have no equivalent in static formats
- HTML in a figure is replaced by the figure's ``:static:`` image, or a note to see the
  online version; ``:html:`` and ``:htmlblock:`` are replaced by their ``:alt:``
- Some cross-reference patterns may not survive the conversion


Import (other formats to RSM)
-----------------------------

``rsm import`` converts a document in any Pandoc-supported format to RSM source.

**Supported input formats**: ``markdown``, ``latex``, ``docx``, ``epub``,
``rst``, ``html``, and any other format Pandoc supports.

**Pipeline**: source file → Pandoc JSON AST → RSM source text.

**Limitations**:

- Pandoc's AST is less expressive than RSM's; imported documents may need
  manual adjustment for RSM-specific features (structured proofs, handrails)
- Bibliography entries are converted to RSM's BibTeX subset where possible
- Document-level metadata (title, authors) is mapped to RSM tags


See also
--------

- :ref:`converting-guide` for practical workflows
- :ref:`ref-cli` for the options of each command
