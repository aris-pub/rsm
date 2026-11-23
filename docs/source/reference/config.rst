.. _ref-config:

Document settings
=================

Settings for the whole document go in the meta keys of one ``:config:``
block, near the top of the document.


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

:ref:`Title <tag-title>`, :ref:`Citation <tag-cite>`.
