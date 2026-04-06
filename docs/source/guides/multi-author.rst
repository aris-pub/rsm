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

Use ``:note:`` to add equal contribution markers, corresponding author
designations, or other annotations:

.. rsm::

   # Noted Authors

   :author: {
     :name: Alice Smith
     :affiliation: Example University
     :note: Equal contribution
   } ::

   :author: {
     :name: Bob Jones
     :affiliation: Example University
     :note: Equal contribution
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

When a manuscript has six or more authors, RSM automatically collapses the
author list to show only the first few, with an expandable "et al." link that
reveals the full list.

.. tip::

   Combine ``:affiliation:``, ``:note:``, and ``:orcid:`` as needed. RSM
   handles the numbering and grouping of shared affiliations and notes
   automatically.
