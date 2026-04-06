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


.. _whats-wrong-with-latex-pdf:

What's wrong with LaTeX + PDF?
******************************

There's nothing inherently wrong with writing scientific manuscripts in LaTeX and
publishing them in PDF format.  However, the LaTeX ecosystem was designed at a time
where the main medium of scientific publication was physically printed books and
magazines.  Today, this is far from the truth as more and more scientists read (and
write) papers online.  The PDF format and many of LaTeX's features are designed to
output documents that will be physically printed, and this is not necessarily the best
option when reading a digital document.  These are some of the problems that arise when
reading PDFs on a digital device:

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


What's wrong with Markdown?
***************************

There's nothing inherently wrong with writing a scientific manuscript in Markdown and
then using some tool to render it into a fully-featured web page.  In fact, some modern
tools such as `Quarto <https://quarto.org/>`_ are based on (extensions of) the Markdown
language.  However, ReStructured Manuscripts uses its own language for a number of
reasons.

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


What's wrong with ReST?
***********************

ReStructured Text (ReST) is another popular markup language used primarily by the
`Sphinx <https://www.sphinx-doc.org/>`_ documentation builder and static site generator.
The first version of RSM was in fact implemented as an extension to ReST, and used
Sphinx in the back end.  However, this quickly became unsustainable as having the core
features of the language be implemented as Sphinx extensions made development, testing,
and overall developer experience awful.  Furthermore, those extensions were already
going beyond what is reasonable to implement as a language extension.  Instead, we
decided to create a new language, taking the best of both Markdown and ReST.  The name
ReStructured Manuscripts is a nod to its roots in ReStructured Text, as well as a nod to
structured proofs, the way that RSM handles mathematical writing in manuscripts.


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
