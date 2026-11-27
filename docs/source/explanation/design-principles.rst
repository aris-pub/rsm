.. _design-principles:

What an RSM page looks like, and why
====================================

An RSM page should read like a well set paper. Everything else that the page
can do comes after that. This page explains the choices that follow from it.


It looks like a paper
---------------------

An RSM page is one column of text, set for reading, with the math, the
theorems and the figures in their places, as in a paper. It has as little
interface as possible: no toolbars, no buttons in the text, no badges. The
controls of a block, its handrail, show only when the pointer is over the
block. The sidebar is closed until the reader opens it.

On a touch screen there is no pointer to show the controls, so the handrail
of each block shows a small menu button all the time, and nothing else.


Tags say what a part is, not how it looks
-----------------------------------------

``:theorem:``, ``:ref:`` and ``:cite:`` say what a part of the document is,
and RSM decides how to show it: the number, the text of a reference, the
tooltip, the place in the table of contents. Because of this:

- the features of the page, such as tooltips, folding and the proof views,
  come from the tags, with no extra work by the author,
- a screen reader can name a block, as in "Theorem 1.1", and the buttons
  that fold it,
- the look of every RSM page can improve without any change to the
  documents.


The look comes with RSM
-----------------------

Every RSM page is styled by BRAIID, the design system of RSM, so the author
does not choose fonts, colors or spacing. BRAIID is made for papers: type
that mixes text and math, a layout for phones and one for computers, a dark
theme, and the handrails. The same look carries over to exported LaTeX and
PDF. An author can still add their own CSS (see :ref:`styling`).


The reader can change it
------------------------

Readers differ: some read on a phone, some need larger type or more
contrast, some read with a screen reader or with the keyboard only. With the
sidebar, the reader can change the typeface, including a typeface made for
low vision, the size of the type, the line height, the width of the column
and the theme. The page can be read with the keyboard only (see
:ref:`reading-keyboard`).


It works without JavaScript
---------------------------

JavaScript adds the features to a page that is complete without it. With
JavaScript turned off, the text, the headings, the figures, the tables, the
citations and the list of references all show, every block is open, and math
shows as its LaTeX source. A page stays readable when it is archived,
printed, or opened where scripts are blocked.


It is a set of files
--------------------

A built page is a set of static files: HTML, CSS, JavaScript and images. It
needs no server that runs code and no account, so it can be put on any web
server, sent as one file (with ``--standalone``), or kept in an archive. An
RSM document does not run the code of the research. An interactive figure is
made beforehand, with a library such as Plotly, and added as a piece of HTML
with a still image beside it (see :ref:`guide-interactive-figures`).
