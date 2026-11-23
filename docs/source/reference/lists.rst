.. _ref-lists:

Paragraphs and lists
====================

A paragraph is text between blank lines, and needs no tag. A list belongs to
the paragraph that it is in, and a list on its own forms a paragraph of its
own.

Every tag on this page takes the meta keys that all tags take, such as
``:label:``. See :ref:`ref-meta-keys`.


.. _tag-paragraph:

.. rst-class:: tag-card

Paragraph ``:paragraph:``
-------------------------

A paragraph with meta keys. A paragraph needs the tag only to take meta keys,
which go in braces right after it. The paragraph ends at the next blank line,
with no closing ``::``.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :paragraph: {:title: <title>} <text>

.. rubric:: Meta keys

``:title:``
   A run-in title in bold, at the start of the paragraph.

.. rubric:: Example

.. rsm::

   :paragraph: {:title: Idea} Pair each even number with its half.

   The next paragraph needs no tag.

.. rubric:: Related

:ref:`Lists <tag-itemize>`.


.. _tag-itemize:
.. _tag-enumerate:

.. rst-class:: tag-card

Lists ``:itemize:`` ``:enumerate:``
-----------------------------------

A list with bullets, and a numbered list. Each item starts with ``:-:``.
``:--:`` makes an item one level deeper, and ``:---:`` two levels deeper.
Items are separated by blank lines, and the list ends with ``::``.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :itemize:
     :-: <item>

     :--: <nested item>
   ::

.. rubric:: Example

.. rsm::

   The steps are:

   :enumerate:
     :-: Write the numbers from 2 to $n$.

     :-: Cross out the multiples of each prime,

     :--: first those of 2,

     :--: then those of 3.
   ::

.. rubric:: Related

:ref:`List items <tag-item>`, :ref:`Paragraph <tag-paragraph>`.


.. _tag-item:

.. rst-class:: tag-card

List items ``:-:`` ``:--:`` ``:---:``
-------------------------------------

One item of a list, at the first, second or third level. Meta keys go in
braces right after the marker. An item holds text and inline markup, and ends
at the next blank line.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :itemize:
     :-: {:label: <label>} <text>
   ::

.. rubric:: Related

:ref:`Lists <tag-itemize>`.
