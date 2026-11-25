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

Notes are rendered as symbols after the author name, with the note text
displayed in a footnote below the author block.


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
button shows every author.

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

.. tip::

   Combine ``:affiliation:``, ``:author-note:``, and ``:orcid:`` as needed. RSM
   handles the numbering and grouping of shared affiliations and notes
   automatically.
