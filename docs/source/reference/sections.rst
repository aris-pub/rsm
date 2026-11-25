.. _ref-sections:

Sections and headings
=====================

A line that starts with ``#`` and a space is the title of the document. The
title must be the first line of the document. Only blank lines, comments and a
``:config:`` block (see :ref:`ref-config`) may come before it. Sections,
subsections and subsubsections are numbered 1, 1.1 and 1.1.1. A section runs
until the next heading of the same level or higher, so it has no closing
``::``.

Every tag on this page takes the meta keys that all tags take, such as
``:label:`` and ``:nonum:``. See :ref:`ref-meta-keys`.


.. _tag-heading:

.. rst-class:: tag-card

Headings ``#`` ``##`` ``###`` ``####``
--------------------------------------

The title of the document, and the start of a section, a subsection or a
subsubsection. Meta keys go in braces after the heading text.

.. rubric:: Syntax

.. rsm::
   :source-only:

   # <document title>

   ## <section title> {:label: <label>}

   ### <subsection title>

   #### <subsubsection title>

.. rubric:: Example

.. rsm::

   # Odd and even

   ## Sums {:label: sec-sums}

   ### Two numbers

   Text.

   ## Notes {:nonum:}

   :ref:sec-sums:: has one subsection.

.. rubric:: Related

:ref:`Section tags <tag-section>`, :ref:`Appendix <tag-appendix>`.


.. _tag-section:
.. _tag-subsection:
.. _tag-subsubsection:

.. rst-class:: tag-card

Section tags ``:section:`` ``:subsection:`` ``:subsubsection:``
---------------------------------------------------------------

The same sections as ``##``, ``###`` and ``####``, written as tags. The title
goes in ``:title:``. As with ``##``, the section runs until the next section,
with no closing ``::``.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :section: {:title: <title>, :label: <label>}

   <content>

.. rubric:: Meta keys

``:title:``
   The title of the section.

.. rubric:: Related

:ref:`Headings <tag-heading>`.


.. _tag-appendix:

.. rst-class:: tag-card

Appendix ``:appendix:``
-----------------------

Marks where the appendix starts. The sections after it are lettered A, B, C,
and their subsections A.1, A.2. The tag stands alone, with no content and no
closing ``::``.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :appendix:

   ## <first appendix section>

.. rubric:: Related

:ref:`Headings <tag-heading>`.


.. _tag-toc:

.. rst-class:: tag-card

Table of contents ``:toc:``
---------------------------

A table of contents of the sections of the document, placed where the tag
is. The reader can switch it between a list and a graph that shows which
sections refer to which. The tag holds no content, and ends with ``::``.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :toc: {:view: tree} ::

.. rubric:: Meta keys

``:view:``
   ``list`` shows the list first, and ``tree`` shows the graph first. The
   default is ``list``.

``:orientation:``
   ``vertical`` or ``horizontal``, the direction of the graph. A horizontal
   graph is shown only on screens at least 768 pixels wide, and a vertical one
   on smaller screens. The default is ``vertical``.

The ``:toc-depth:`` key of the ``:config:`` block sets how many heading levels
the list shows: ``1`` shows sections only, ``2`` adds subsections and ``3``
adds subsubsections. Without it, the list shows every level. The graph shows
every level.

.. rubric:: Related

:ref:`Headings <tag-heading>`, :ref:`Document settings <tag-config>`,
:ref:`reading-sidebar`.
