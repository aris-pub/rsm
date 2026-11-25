.. _ref-config:

Document settings
=================

Settings for the whole document go in the meta keys of one ``:config:``
block. The block can go anywhere in the document. It is the only block that
can go before the title.


.. _tag-config:

.. rst-class:: tag-card

Settings ``:config:``
---------------------

A block that holds only meta keys and shows nothing in the page. It ends with
``::`` after the braces.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :config: {
     :numbering: document
   }
   ::

.. rubric:: Meta keys

``:accent:``
   The accent color of the page: ``blue`` (the default), ``red``, ``green``,
   ``orange``, ``yellow``, ``purple``, ``pink`` or ``gray``.

``:typography:``
   The typeface of the text: ``sans-serif`` (the default) or ``serif``.

``:numbering:``
   How blocks are numbered: ``section`` (the default) numbers them within
   each section, as in Theorem 2.1, ``document`` numbers them through the
   whole document, as in Theorem 7, and ``none`` numbers nothing.

``:citation-style:``
   How citations look: ``numeric`` (the default), as in [1],
   ``parens-author-year``, as in (Knuth, 1998), or ``author-parens-year``, as
   in Knuth (1998). In the two author and year styles, the list of references
   has no numbers and is sorted by author and then year.

``:lang:``
   The language of the document, as a code such as ``en`` (the default),
   ``es`` or ``en-US``. Screen readers use it.

``:override-date:``
   A date shown under the title, as ``YYYY-MM-DD``. Without it, the page
   shows no date.

``:eyebrow:``
   A short line of text above the title, such as "Preprint".

``:no-minimap:``
   Turns off the map of the page that replaces the scroll bar, and keeps the
   browser's own scroll bar. See :ref:`reading-minimap`.

``:author-display-first:``
   How many authors to show at the start of a long list of authors, as a
   whole number such as ``3``. The page shows the first authors, a button
   that reads "5 more" (the number of authors not shown) and the last
   authors set by ``:author-display-last:``. A click on the button shows
   every author. When only one of the two keys is given, the other one is 0.
   When neither is given, or when the two numbers add up to the number of
   authors or more, the page shows every author. Readers without
   JavaScript always see every author.

``:author-display-last:``
   How many authors to show at the end of a long list of authors, as a whole
   number such as ``2``. See ``:author-display-first:``.

``:toc-depth:``
   How many heading levels the list in each table of contents shows: ``1``
   shows sections only, ``2`` adds subsections and ``3`` adds subsubsections.
   Without it, the list shows every level. The graph of the table of contents
   and the sidebar show every level. See :ref:`tag-toc`.

``:plain-title:``
   The title as plain text, for the browser tab, when the title holds math or
   other markup. Without it, the tab shows the title with each piece of math
   as its LaTeX between dollar signs.

.. rubric:: Example

.. rsm::

   # Graphs with $n$ vertices

   :config: {
     :eyebrow: Preprint
     :override-date: 2024-01-15
     :plain-title: Graphs with n vertices
   }
   ::

   ## Results

   :theorem:
   A graph with $n$ vertices has at most $n(n-1)/2$ edges.
   ::

.. rubric:: Related

:ref:`Title <tag-title>`, :ref:`Citation <tag-cite>`,
:ref:`Table of contents <tag-toc>`.
