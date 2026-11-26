.. _multi-author-guide:
.. _guide-front-matter:

Authors and front matter
========================

The front matter of an RSM document is its title, its authors and its
abstract. RSM lays them out at the top of the page, numbers the affiliations,
and folds the details that a reader rarely needs under one line.

This page builds the front matter of one short document. The tags are listed
in :ref:`ref-front-matter`.


The whole front matter
----------------------

.. rsm::

   # Graphs without triangles

   :author: {
     :name: Ada Lovelace
     :affiliation: University of London
     :email: ada@example.org
     :orcid: 0000-0002-1825-0097
     :author-note: Equal contribution
   } ::

   :author: {
     :name: Bo Chen
     :affiliation: ETH Zurich
     :author-note: Equal contribution
   } ::

   :author: {
     :name: Cy Diaz
     :affiliation: University of London
   } ::

   :abstract: {:keywords: graphs, triangles, extremal, :msc: 05C35}
   We give a short proof of Mantel's theorem.
   ::

   ## Results

   A graph on $n$ vertices with no triangle has at most $n^2/4$ edges.

The rest of this page goes through the parts of this front matter.


The title
---------

The first line that starts with ``#`` and a space is the title of the
document. Only blank lines, comments and a ``:config:`` block may come before
it.


Add the authors
---------------

Write one ``:author:`` block for each author, after the title, in the order
in which the names should appear. All the information goes in the meta keys,
so each block ends with ``::`` right after the closing brace.

- ``:name:`` is the name, as it should be printed.
- ``:affiliation:`` is the institution. Authors with the same affiliation text
  share one number, so write it the same way each time.
- ``:email:`` adds a mail icon next to the name, and a "Correspondence" line
  with the address under the authors.
- ``:orcid:`` adds an ORCID icon next to the name, linked to the author's
  ORCID record.
- ``:author-note:`` adds a note, such as "Equal contribution". The notes are
  listed under the authors, once each.


Shorten a long list of authors
------------------------------

By default the page lists every author. To show only the first and the last
few, set ``:author-display-first:`` and ``:author-display-last:`` in the
``:config:`` block:

.. rsm::

   # A large collaboration

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

The page shows the first two names, a "3 more" button, and the last name.
When only one of the two keys is given, the other one is 0. When the two
numbers add up to the number of authors or more, every author is shown.


Add the abstract
----------------

The ``:abstract:`` block comes after the authors. It is headed "Abstract", and
its ``:keywords:`` and ``:msc:`` (Mathematics Subject Classification codes)
are listed under its text, each separated by commas.


What the reader can do
----------------------

The author block has two states, closed and open. It is closed when the
reader first opens the page, and the page remembers the reader's choice.

- Closed, the block shows the names (only the first and last ones when the
  list is shortened) and, at the foot of its rail, a line that counts the
  details, such as "2 affiliations · 1 email · 1 ORCID · 1 note", as a folded
  proof counts its steps.
- Open, it shows every name and the details: the numbered affiliations, the
  notes, the correspondence address and the ORCID iDs.
- The arrow to the left of the block, the "3 more" button and the line at the
  foot open the block. The arrow and the "Show fewer" button close it. A block
  with nothing to open has no arrow.
- Pointing at an author's name, or tapping it on a phone, shows that author's
  affiliation and note in a tooltip. Pointing at an affiliation number shows
  that affiliation.
- The mail and ORCID icons next to a name link to the author's address and
  ORCID record.

Readers without JavaScript see every name and all the details.
