.. _why-rsm:

Why RSM
=======

RSM exists because most papers are now read on screens, while the tools for
writing them still make printed pages. This page explains what that costs the
reader, and why RSM is a language of its own instead of an extension of
another one.


A web page instead of a PDF
---------------------------

A PDF has a fixed page size, a fixed layout and a fixed typeface. It reads
well on the screen that it was set for, and badly on a phone, where the reader
zooms and scrolls sideways. A reader who needs larger type, another typeface
or more contrast cannot get them without other tools.

An RSM page is a web page. Its layout follows the width of the screen, and
the reader can switch to dark mode. With the sidebar, the reader can also
change the typeface, the size of the type and the line height. Because RSM knows what each part of the document is,
the page can also do things that a PDF cannot:

- show a theorem, an equation or a reference in a tooltip, without leaving the
  current place,
- fold and open sections, proofs and proof steps,
- show how the steps of a proof depend on each other, and which assumptions
  hold at each step.

See :ref:`reading` for all of them.

LaTeX lays out a fixed page better than any web browser does. RSM does not
compete with it there: it makes pages whose layout changes with the screen,
and CSS, the layout language of the web, is made for that.


When another tool fits better
-----------------------------

- **A journal that wants LaTeX or a PDF.** RSM can export to LaTeX and PDF
  through pandoc (see :ref:`ref-cli`), but it has no journal templates.
- **A document that runs code.** An RSM document does not run code when it is
  built. It can hold a chart made elsewhere, as an HTML file. For documents
  that run Python, R or Julia, tools such as Jupyter and Quarto fit better.
- **Short documents without math.** Markdown is simpler and needs no new
  tool.


Why a new language
------------------

**Not Markdown.** Markdown is popular because it has very little syntax.
Papers need much more: labels on any part, numbered theorems, proofs,
citations, meta keys. Adding all of them to Markdown would remove what makes
Markdown simple, and the result would be a new language that looks like
Markdown but does not behave like it.

**Not reStructuredText.** RSM began as an extension of reStructuredText and
Sphinx. Its main features did not fit the extension system, and testing them
was slow and hard, so RSM became a language of its own.

RSM is built around the parts of a paper: sections, theorems, proofs, steps,
equations, figures, references and citations are each a tag, with a label
that links to it. See :ref:`ref-syntax-basics`.
