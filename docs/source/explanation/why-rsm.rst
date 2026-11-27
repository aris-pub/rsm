.. _why-rsm:

Why RSM
=======

Most papers are now read on screens, but most of them are still written to
be printed. RSM is a language for papers that are read on screens first. This
page explains what that changes for the reader, why RSM is a new language,
and when another tool fits better.


Screens instead of paper
------------------------

A PDF is a printed page shown on a screen. It has a fixed width, a fixed
layout and a fixed typeface. On a laptop it reads well enough. On a phone,
the reader zooms in and scrolls sideways along every line. A reader who needs
larger type, more contrast or a dark background has no way to get them.

An RSM document is a web page. The text fits the width of the screen, and
the reader can change the typeface, the size and the theme. The page is
also built from what the author wrote: RSM knows which part is a theorem,
which is its proof, which steps the proof has and which earlier steps each
one uses. With that, the page can do things that a printed page cannot:

- show a theorem or an equation in a tooltip, where it is cited, so the reader
  keeps their place,
- fold a proof down to its main steps and open only the ones the reader wants,
- show which steps a step uses, and what is assumed and left to prove at it,
- let the reader rename a symbol, everywhere in the paper at once.

See :ref:`reading` for all of them. A printed copy is still there when it is
needed: RSM exports to LaTeX and PDF (see :ref:`converting-guide`).


Why a new language
------------------

A page that does these things needs a source that says what each part of the
document is. The existing languages do not say it, or say it only in part.

**LaTeX** describes how to set a page. Theorems, proofs and labels exist as
commands that different packages define in different ways, and the steps
inside a proof are only paragraphs of text. A program that reads LaTeX source
cannot tell reliably what each part is.

**Markdown** is popular because it has very little syntax. Papers need much
more: labels on any part, numbered theorems, proofs with steps, citations,
footnotes. Adding all of them to Markdown would take away what makes it
simple, and the result would look like Markdown without behaving like it.

**reStructuredText** was RSM's starting point: the first versions of RSM were
an extension of reStructuredText and Sphinx. RSM's main features did not fit
the extension system, and testing them was slow and hard, so RSM became a
language of its own.

In RSM, each part of a paper is a tag: sections, theorems, proofs, steps,
equations, figures, references and citations. Any of them can have a label,
and a reference to the label links to it. See :ref:`ref-syntax-basics`.


When another tool fits better
-----------------------------

- **A journal that wants its own LaTeX template.** RSM exports to LaTeX and
  PDF, with its own look, but it has no journal templates.
- **A document that runs code.** An RSM document does not run code when it is
  built. It can hold a chart made elsewhere (see
  :ref:`guide-interactive-figures`). For documents that run Python, R or
  Julia, tools such as Jupyter and Quarto fit better.
- **A short document without math or proofs.** Markdown is simpler, and
  needs no new tool.
