.. _multi-author-guide:

Writing Multi-Author Papers
============================

This guide covers setting up multiple authors with affiliations, notes, and
ORCID identifiers.


Multiple authors
----------------

Add one ``:author:`` block per author:

.. rsm::

   # Collaborative Research

   :author: {
     :name: Alice Smith
     :affiliation: Example University
   } ::

   :author: {
     :name: Bob Jones
     :affiliation: Example University
   } ::

   ## Introduction
   Our joint work shows that...

Authors sharing the same affiliation text are grouped automatically with a
shared superscript number.


Different affiliations
----------------------

.. rsm::

   # Cross-Institution Study

   :author: {
     :name: Alice Smith
     :affiliation: Example University
   } ::

   :author: {
     :name: Carlos Garcia
     :affiliation: Other Institute
   } ::

   ## Introduction
   Combining perspectives from both
   institutions...


Author notes
------------

Use ``:author-note:`` to add equal contribution markers, corresponding author
designations, or other annotations:

.. rsm::

   # Noted Authors

   :author: {
     :name: Alice Smith
     :affiliation: Example University
     :author-note: Equal contribution
   } ::

   :author: {
     :name: Bob Jones
     :affiliation: Example University
     :author-note: Equal contribution
   } ::

   ## Introduction
   This is a joint work.

When the authors have more than one note, each note gets a symbol after the
author name. The note text is in the author details (see
:ref:`multi-author-reader`).


ORCID identifiers
------------------

Add an ORCID iD to link to the author's ORCID profile:

.. rsm::

   # With ORCID

   :author: {
     :name: Alice Smith
     :affiliation: Example University
     :orcid: 0000-0001-2345-6789
   } ::

   ## Introduction
   Research with verified identity.


Large author lists
------------------

By default the page lists every author. To shorten a long list, set
``:author-display-first:`` and ``:author-display-last:`` in the ``:config:``
block. The page then shows the first and last authors and, between them, a
button that reads "3 more" (the number of authors not shown). A click on the
button opens the author block: it shows every author, with a "Show fewer"
button where the hidden authors end, and the author details. A click on "Show
fewer" closes the block again.

.. rsm::

   # Graphs without triangles

   :config: {
     :author-display-first: 2
     :author-display-last: 1
   }
   ::

   :author: {:name: Ada Lovelace} ::

   :author: {:name: Bo Chen} ::

   :author: {:name: Cy Diaz} ::

   :author: {:name: Dana Patel} ::

   :author: {:name: Eli Novak} ::

   :author: {:name: Fay Okafor} ::

When only one of the two keys is given, the other one is 0. When the two
numbers add up to the number of authors or more, the page shows every author.
Readers without JavaScript always see every author.

.. _multi-author-reader:

What the reader can do
----------------------

In the built page, the author block is closed when the reader first opens the
page. The page remembers whether the reader left the block open or closed, so
the block is the same after a reload. Closed, it
shows the names (only the first and last ones when the list is shortened) and,
at the foot of the rail, a line that counts the affiliations, emails, ORCID iDs and
notes, such as "4 affiliations · 1 email · 1 ORCID · 1 note".

- A click on the label, on the "3 more" button, or on the arrow to the left of
  the block opens the block. Open, it shows every name and the details: the
  numbered affiliations, the notes, the correspondence address and the ORCID
  iDs.
- A click on the arrow, or on the "Show fewer" button, closes the block. The
  arrow turns as on any other folded block. On a
  touch screen the arrow is not shown, and the block's menu has an Expand or
  Collapse item instead. A block that has nothing to open (every author is
  shown and there are no affiliations, emails, ORCID iDs or notes) has no
  arrow.
- Pointing at an author's name, or tapping it on a phone, shows that author's
  affiliation and note in a tooltip. Pointing at a superscript number shows
  its affiliation.

Readers without JavaScript see every name and all the details, with no
buttons.

.. tip::

   Combine ``:affiliation:``, ``:author-note:``, and ``:orcid:`` as needed. RSM
   handles the numbering and grouping of shared affiliations and notes
   automatically.
