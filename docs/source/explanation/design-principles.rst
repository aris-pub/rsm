.. _design-principles:

Design principles
=================

These principles decide what RSM does and what it leaves out.


.. _web-first:

The page is the main output
---------------------------

RSM makes web pages first. HTML is a standard that every browser reads, and
old HTML pages still open today. RSM can also export to PDF, LaTeX and other
formats through pandoc, for readers and journals that need them.


.. _semantic-markup:

Tags say what a part is, not how it looks
-----------------------------------------

``:theorem:``, ``:ref:`` and ``:cite:`` say what a part of the document is.
RSM decides how to show it: the number, the link text, the tooltip, the place
in the table of contents. Because of this:

- screen readers can say "Theorem 1" instead of guessing from the styling,
- tooltips, folding and the sidebar come from the tags, with no extra work by
  the author,
- the look of all RSM pages can change without changing any document.


The look comes with RSM
-----------------------

Every RSM page is styled by BRAIID, the design system of RSM. The author does
not need to choose fonts, colors or spacing. BRAIID is made for papers: type
for mixed math and text, handrails that show the structure of the document,
layouts for phones and computers, and dark mode. An author can still add their
own CSS (see :ref:`styling`).


.. _progressive-enhancement:

The page works without JavaScript
---------------------------------

JavaScript adds features to a page that is complete without it. With
JavaScript turned off, all text, headings, figures, tables, citations and the
list of references still show, and math shows as its LaTeX source. Tooltips, folding, the sidebar and the
scroll bar map need JavaScript. A page stays readable when it is archived,
printed or opened where scripts are blocked.


.. _static-documents-not-executable-notebooks:

A document does not run code
----------------------------

An RSM document and the code of the research are separate. A document can
hold an interactive chart, made beforehand with a library such as Plotly, as
an HTML file, with a still image for the places where HTML cannot show (see
:ref:`tutorial-figures`). A built page is a set of static files: it needs no
server that runs code, and it does not break when the libraries of the
research change.


.. _humane-design:

Little on the screen, good defaults
-----------------------------------

- Controls show when they are needed. On a computer, a handrail shows only
  when the pointer is over its block.
- ``rsm build`` makes a complete page with no settings. Numbering, colors,
  typography and dark mode work from the start.
- RSM is a command that reads text files and writes web pages. It needs no
  account.
