.. _special:

Special tags
============

All tags may be introduced using the ``:tag-name: <contents> ::`` notation.  However,
some tags admit an alternative notation.


Shorthand
*********

Some tags allow for *shorthand* notation.  Shorthand notation does not need tag names or
Halmoses to modify the contained text, it uses different delimiters instead.  For
example, the following are two different ways for introducing bold text, one using the
standard ``:span:`` tag and another using shorthand notation and double asterisks ``**``.

.. rsm::

   This text is :span: {:strong:} bold ::, as
   is **this one**.

Similarly, italic text also has a shorthand version using single asterisks ``*``.

.. rsm::

   This text is :span: {:emphas:} italic ::,
   as is *this one*.

Math tags allow shorthand notation using one dollar sign ``$`` for inline and two ``$$``
for blocks.

.. rsm::

   Either :math:2 + 2 = 4:: or
   $2 + 2 = 4$.

.. rsm::

   Either
   :mathblock:
   2 + 2 = 4
   ::
   or
   $$
   2 + 2 = 4.
   $$

Code allows shorthand notation using one backtick ````` for inline or three ``````` for blocks.

.. rsm::

   Either :code:var = "value":: or
   `var = "value"`.

.. rsm::

   Either

   :codeblock:
   var = "value"
   ::

   or

   ```
   2 + 2 = 4.
   ```

.. grid:: 1 1 1 2

   .. grid-item::

      .. tip::

         Either standard or shorthand notation allow meta tags.  For example, to assign a
         label to an inline math region, you may use either ``:math:{:label:some-lbl} 2+2=4
         ::`` or ``${:label:some-lbl} 2+2=4 $``.

   .. grid-item::

      .. tip::

         The standard notation using colons and Halmos as delimiters is easy to parse by
         automated tools.  The shorthand notation is easy to read by humans.


The Appendix Stamp
******************

Some tags deviate from the standard ``:tag-name: <contents> ::`` syntax in that they do
not allow contents nor need a closing Halmos. These are called *stamp* tags. One example
is the ``:appendix:`` tag, whose role is to mark the place in the manuscript where the
Appendix starts.

.. rsm::

   ## First section

   ## Second section

   :appendix:

   ## First appendix

Among other things, the ``:appendix:`` stamp restarts the numbering of the following
sections and changes it from numbers to letters.


Paragraphs
**********

Paragraphs of text need no tag. However, if you want to refer to an entire paragraph of
text, you need to add a label. Labels can only be specified in meta tags, and meta tags
can only go immediately after the opening tag of a block or inline. Then how can we
label a paragraph of text?

The ``:paragraph:`` tag exists for this reason. It does not need a closing Halmos after
the paragraph contents.

.. rsm::

   :paragraph: {:label:my-para} This is how
   you refer to a paragraph of text.

   And now we refer to the entire previous
   :ref:my-para,paragraph::.


Configuration
*************

The ``:config:`` block sets document-level configuration. It accepts metadata but has no
content and does not appear in the rendered output.

.. rsm::

   # My Manuscript

   :config: {
     :override-date: 2024-01-15
     :numbering: section
   }
   ::

   ## Introduction
   Content here.

The ``:override-date:`` key sets the manuscript date (format: YYYY-MM-DD). The
``:numbering:`` key controls how theorems and similar blocks are numbered:

- ``section`` - Numbers reset per section (Theorem 1.1, 1.2, 2.1, ...)
- ``document`` - Numbers increment across the entire document (Theorem 1, 2, 3, ...)
- ``none`` - No automatic numbering

The config block can appear anywhere in the document (typically at the top) and only one
config block is allowed per manuscript.
