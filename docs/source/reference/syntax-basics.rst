.. _ref-syntax-basics:

Syntax basics
=============

An RSM file is plain text. Paragraphs are separated by blank lines, and most
of the markup is made of tags: words between colons, such as ``:theorem:``.


Blocks and inline tags
----------------------

A **block** is a part of the document of its own, such as a theorem, a
figure or a list. It starts with its tag and ends with ``::``, and can hold
paragraphs and other blocks.

.. rsm::
   :source-only:

   :remark:
   <paragraphs and blocks>
   ::

An **inline tag** marks a piece of text inside a paragraph, such as a
reference or a span. It also ends with ``::``.

.. rsm::
   :source-only:

   Text with :span: {:strong:} <words> :: in it.

A few tags are written differently:

- Headings start with ``#``, ``##``, ``###`` or ``####``, and a section runs
  until the next heading. See :ref:`ref-sections`.
- ``$...$``, ``$$...$$``, ``**...**``, ``*...*`` and backticks are short
  forms for math, bold, italic and code. See :ref:`ref-math-code` and
  :ref:`ref-inline`.
- List items start with ``:-:`` and end at the next blank line. See
  :ref:`ref-lists`.
- ``:appendix:``, ``:qed:``, ``:prev:``, ``:prev2:`` and ``:prev3:`` stand
  alone, with no ``::``.


Meta keys
---------

Meta keys go in braces right after a tag, and add information to it, such as
a label or a title. See :ref:`ref-meta-keys`.

.. rsm::

   :theorem: {:label: thm-two, :title: Two is prime}
   The number 2 is prime.
   ::

   :ref:thm-two:: is short.


Special characters
------------------

A word between colons is read as a tag, and an unknown tag is an error. To
write a colon, a dollar sign or an asterisk as itself where RSM would read it
as markup, put a backslash before it: ``\:``, ``\$``, ``\*``. A colon between
digits or letters, as in 3:4, needs no backslash.

``%`` starts a comment, which runs to the end of the line. To write a percent
sign, write ``\%``.

.. rsm::

   The tag \:theorem\: starts a theorem. It costs \$5, or 50\% off.
