.. _ref-front-matter:

Title, authors and abstract
===========================

The first lines of a document: its title, its authors and its abstract.
Settings for the whole document, such as a date under the title, go in
``:config:``. See :ref:`ref-config`.


.. _tag-title:

.. rst-class:: tag-card

Title ``#``
-----------

The title of the document, on the first line, after ``#`` and a space. It can
hold inline markup, such as math.

.. rubric:: Syntax

.. rsm::
   :source-only:

   # <title>

.. rubric:: Related

:ref:`Headings <tag-heading>`, :ref:`Document settings <tag-config>`.


.. _tag-author:

.. rst-class:: tag-card

Author ``:author:``
-------------------

One author of the document. Write one ``:author:`` for each author, after the
title. The page lists the names, with a mail icon and an ORCID icon for the
authors who have them. The block starts folded, and at the foot of its rail
a line counts the affiliations, emails, ORCID iDs and notes, such as
"2 affiliations · 1 email", as a folded proof counts its steps. A click on
that line, or on the arrow to the left of the block, opens the block: the
line is replaced by the numbered affiliations, the notes, the correspondence
address and the ORCID iDs. The arrow closes the block again. Pointing at a
name, or tapping it on a phone, shows that author's affiliation and note in a
tooltip. Readers without JavaScript see all of it.
All the information is in the meta keys, so the block ends with ``::`` right
after the braces.
To show only the first and last authors of a long list, use
``:author-display-first:`` and ``:author-display-last:`` in
:ref:`Settings <tag-config>`.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :author: {
     :name: <name>
     :affiliation: <affiliation>
   } ::

.. rubric:: Meta keys

``:name:``
   The name of the author.

``:affiliation:``
   The institution of the author.

``:email:``
   An email address, linked from the mail icon next to the name.

``:orcid:``
   An ORCID iD, such as ``0000-0002-1825-0097``, linked from the ORCID icon
   next to the name.

``:author-note:``
   A note on the author, such as "Equal contribution".

.. rubric:: Example

.. rsm::

   # Sums of even numbers

   :author: {
     :name: Ada Lovelace
     :affiliation: University of London
     :email: ada@example.org
   } ::

   :author: {
     :name: Charles Babbage
     :affiliation: University of Cambridge
   } ::

.. rubric:: Related

:ref:`Abstract <tag-abstract>`.


.. _tag-abstract:

.. rst-class:: tag-card

Abstract ``:abstract:``
-----------------------

The abstract of the document, after the authors, headed "Abstract".

.. rubric:: Syntax

.. rsm::
   :source-only:

   :abstract: {:keywords: <word>, <word>}
   <text>
   ::

.. rubric:: Meta keys

``:keywords:``
   Keywords, separated by commas, listed under the abstract.

``:msc:``
   Mathematics Subject Classification codes, separated by commas, listed
   under the abstract.

.. rubric:: Related

:ref:`Author <tag-author>`.
