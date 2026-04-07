.. _faq:
.. _why-rsm:

Why RSM?
========

Quick Comparison
****************

RSM compared to popular alternatives:

.. list-table::
   :header-rows: 1
   :widths: 15 17 17 17 17 17

   * - Feature
     - RSM
     - LaTeX + PDF
     - Markdown
     - ReStructuredText
     - Quarto
   * - **Output format**
     - HTML
     - PDF
     - HTML (via converter)
     - HTML (via Sphinx)
     - HTML, PDF, etc.
   * - **Responsive design**
     - Yes (automatic)
     - No (fixed layout)
     - Yes (depends on theme)
     - Yes (Sphinx themes)
     - Yes (with Quarto)
   * - **Mathematical proofs**
     - Yes (first-class)
     - Yes (amsthm)
     - No (requires extensions)
     - No (requires extensions)
     - Via LaTeX blocks
   * - **Interactive tooltips**
     - Yes (automatic)
     - No
     - No
     - No
     - Limited
   * - **Cross-references**
     - Yes (with tooltips)
     - Yes (hyperref)
     - Limited
     - Yes
     - Yes
   * - **Citations**
     - BibTeX (native)
     - BibTeX (native)
     - Via Pandoc
     - Via sphinxcontrib-bibtex
     - BibTeX (native)
   * - **Syntax complexity**
     - Medium
     - High (steep learning curve)
     - Low (very simple)
     - Medium
     - Medium
   * - **Semantic tags**
     - Yes (core feature)
     - No (presentational)
     - No
     - Partial
     - Partial
   * - **Learning curve**
     - 1-2 hours
     - Weeks to months
     - 30 minutes
     - 1-2 hours
     - 2-3 hours
   * - **Best for**
     - Web-first research
     - Traditional publishing
     - Simple docs
     - Documentation sites
     - Reproducible research

.. admonition:: When to choose RSM

   **Use RSM if**:

   - You want web-native output (not PDF)
   - Your readers use mobile devices or tablets
   - You value interactive references and tooltips
   - You're writing formal mathematics with structured proofs
   - You want semantic markup (content over presentation)

   **Stick with LaTeX if**:

   - Your field requires PDF submissions
   - You already have a LaTeX workflow that works
   - You need journal-specific LaTeX templates
   - You prefer print-oriented layout

   **Consider Quarto if**:

   - You need computational notebooks (R, Python, Julia)
   - You want multiple output formats (HTML, PDF, Word)
   - Your work involves heavy data science

   **Consider Markdown if**:

   - Your documents are simple (no math, no proofs)
   - You want minimal syntax
   - You're writing blogs or READMEs, not research papers


Detailed Comparisons
********************

The following sections explain the design choices behind RSM in detail.


.. _why-not-latex-pdf:

Why not LaTeX + PDF?
********************

LaTeX and PDF remain excellent for print-oriented publishing. However, the LaTeX
ecosystem was designed when the primary medium was physically printed books and
journals. Today, most scientists read papers on screens. The PDF format inherits
several limitations in this context:

1. A PDF file has a fixed geometry (page size, margins, etc), while digital devices
   (laptops, tablets, mobile phones) have a variety of screen sizes and shapes.  The
   same PDF file may be read easily in, for example, a laptop screen, but not in a
   tablet or mobile screen.

2. A PDF file has a fixed layout (the relative positions of text, headers, figures,
   tables, etc).  In contrast, in the last decade, digital documents and especially web
   pages are moving toward being *responsive*, that is, their layout adapts to the
   features of the devices they are being read on.

3. A PDF file has a fixed typography (font family, weight, size, color, etc).  For
   accessibility reasons, a reader may prefer different typographic choices.  For
   example, some font families are designed to be read more easily by people with
   dyslexia, while high-contrast color schemes are preferred by people with certain
   sight conditions.  PDF files cannot adapt to the preferences of the user without
   using external tools.

4. While there are ways to configure LaTeX to output files in a format different than
   PDF (e.g. EPS, DVI), most of the above critiques still hold true.

5. While there are ways to transform the output of LaTeX to a web-ready format
   (i.e. HTML), this is always an extra step that must be done outside of the LaTeX
   ecosystem.  As a result, not all of the LaTeX features translate transparently to the
   final output and some post-processing is sometimes necessary.


Why not Markdown?
*****************

Markdown is a natural starting point for web-native writing. Tools like
`Quarto <https://quarto.org/>`_ extend it for scientific use. RSM chose a
different path for several reasons.

1. One of the main features of RSM is being able to reference any place of the
   manuscript, even single words, and automatically showing tooltips to the referenced
   content.  Markdown does not allow the user to reference arbitrary text in the
   manuscript, and would require non-trivial extensions to do so.

2. Rather than implement RSM's core features as mere language extensions, RSM is a
   language that supports these features as first-class citizens.

3. One of the main benefits of Markdown is its minimal syntax.  There are very few
   special characters and the language basically gets out of the way as much as
   possible.  If RSM had been written as a Markdown extension, it would have been
   unavoidable to add new syntax and more special characters to Markdown.  In so doing,
   we would have countered one of the main benefits of the language.  Instead of making
   "Markdown but not Markdown", we decided to implement our own language.


Why not ReStructuredText?
*************************

RSM started as a Sphinx/ReST extension. The first version used ReST's directive
system and Sphinx as the backend. This became unsustainable: core features
implemented as Sphinx extensions made development and testing painful, and the
extensions were pushing beyond what the directive API could reasonably support.

RSM became its own language, taking the best of both Markdown and ReST. The
name Readable Science Markup reflects its focus on readability and scientific
writing.


Is CSS better than Tex?
***********************

Usually, scientific manuscripts use the TeX engine for page layout (at least those
manuscripts written with LaTeX and related tools).  Instead, RSM being a web-native
format, uses CSS as layout engine.  TeX is widely regarded as some of the best and most
robust and bug-free software ever produced, and is without a doubt better than CSS at
*laying out a page of fixed geometry*.  But therein lies the difference: the purpose of
RSM is to produce manuscripts that are responsive to device, screen size, and user
preferences, and TeX cannot achieve this since it was never designed to do so.  The
standard engine for laying out applications with such requirements is CSS, and it is
undoubtedly the best and most widely available software for doing so.
