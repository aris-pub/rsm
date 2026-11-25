.. _guide-footnotes-asides:

Footnotes and asides
====================

RSM has two kinds of notes. A footnote is numbered and listed at the end of
the document, as in a printed paper. An aside is a short note about a phrase
of the text, with no number, which the reader opens from the phrase or reads
in the margin.

This page builds one short document with both. The tags are listed in
:ref:`Footnote <tag-note>` and :ref:`Aside <tag-aside>`.


The whole document
------------------

.. rsm::
   :sidebar:

   # Graphs without triangles

   ## Results

   A graph on $n$ vertices with no triangle has at most $n^2/4$ edges
   :note:fn-mantel::. The bound is reached by a
   :aside:bip,complete bipartite graph:: with two equal parts.

   :aside: {:label: bip}
   A graph whose vertices are split into two parts, with an edge between every
   pair of vertices in different parts and none inside a part.
   ::

   :note: {:label: fn-mantel}
   This is Mantel's theorem, from 1907.
   ::

The rest of this page goes through the parts of this document.


Add a footnote
--------------

A footnote has two parts:

- The call, ``:note:fn-mantel::``, goes in the text where the number should
  appear, after a space.
- The text of the footnote goes in a ``:note:`` block with the same label.
  The block can be anywhere in the document, for example right after the
  paragraph.

RSM numbers the footnotes 1, 2, 3 in the order of their calls, and lists them
at the end of the document.


Add an aside
------------

An aside also has two parts:

- The call, ``:aside:bip,complete bipartite graph::``, marks a phrase of the
  text: the label, a comma, and the phrase. The phrase can hold inline markup
  and math.
- The text of the aside goes in an ``:aside:`` block with the same label.

Use an aside for a definition or a remark that a reader may need while
reading the phrase, and a footnote for a remark that can wait until the end,
such as a source or a historical note.


What the reader can do
----------------------

In the built page:

- Hovering over a footnote number, or tapping it on a phone, shows the
  footnote in a tooltip. Each footnote at the end of the document links back
  to its call.
- When the window is wide enough, the page has a margin column on the right,
  and each aside sits there, level with its phrase.
- On a narrower window, the reader clicks or taps the phrase of an aside, and
  the aside opens under its paragraph.

Click "Open" above the example at the top of this page to see it in its own
tab, and make the window wide to see the aside in the margin.
