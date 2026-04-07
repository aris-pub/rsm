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

**Supported output formats**: ``latex``, ``pdf``, ``docx``, ``epub``, ``typst``,
``markdown``, ``html``, ``rst``, and any other format Pandoc supports.

**Pipeline**: RSM source → RSM AST → Pandoc JSON AST → target format.

For LaTeX output, RSM includes a custom ``braiid.sty`` package and a Lua filter
(``braiid.lua``) that maps RSM-specific constructs (theorems, proofs, structured
mathematics) to appropriate LaTeX environments.

**Limitations**:

- Interactive features (handrails, tooltips) have no equivalent in static formats
- HTML widgets embedded via ``:html:`` are dropped
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
- :ref:`cli-commands` for command flags
