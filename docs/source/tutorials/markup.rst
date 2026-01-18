.. _markup:

RSM markup
==========

Readable Science Markup (RSM) was inspired by popular languages such as Markdown, ReST,
and LaTeX. RSM strives for simplicity, flexibility, and functionality.

.. rsm::
   Hello, **RSM**!

The main syntax feature of RSM are *tags*. Strings such as ``:rsm:`` are called *tags*.
In RSM, tags are used to annotate regions of text, for example to delimit sections and
other parts of a manuscript. The tag functions as open delimiter, and the empty tag
``::``, a.k.a. *Halmos*, is the closing delimiter.

.. rsm::

   :abstract:
   This is the manuscript's abstract.
   ::

   ## First Section
   And this is the contents of a section.

Some tags are used to add meta-data to the annotated regions.  For example, the
``:section:`` tag in the previous example introduces a new region of the manuscript,
while the ``:title:`` tag directly below it modifies the parent ``:section:`` tag by
specifying its title.  Tags such as this are called *meta* tags.

Tags such as ``:rsm:``, ``:abstract:``, and ``:section:`` introduce parts of the
manuscript that are clearly separated from other parts.  These are called *block* tags.
In contrast, the following example illustrates the ``:span:`` tag.

.. rsm::

   Span tags do not introduce new parts, but
   :span: {:strong:} live within:: their
   parents.

The ``:span:`` tag does not introduce a separate block, but a region of text that lives
within its enclosing parent, in this case a paragraph.  Tags such as this are called
*inline* tags.

Furthermore, in this example we used the ``:strong:`` tag to modify the enclosing ``:span:`` tag,
i.e. ``:strong:`` is a meta tag of ``:span:``.  Note the use of braces to introduce the
``:strong:`` tag and the use of the Halmos ``::`` as closing delimiter of ``:span:``.

The notation ``:span: {:strong:} text ::`` to introduce bold text allows an alternative
*shorthand* notation using asterisks (``*``).  Similarly, the hashtag (``#``) symbol can
be used as shorthand to introduce a section with a title.

.. rsm::

   ## Awesome section

   Span tags do not introduce new parts, but
   *live within* their parents.

Here is a complete example using all the basic features of RSM markup.

.. rsm::

   # RSM Markup

   :author: {
     :name: Melvin J. Blanc
     :affiliation: ACME University
     :email: mel@acme.edu
   } ::

   :abstract:
   Web-first scientific manuscripts.
   ::

   ## Awesome Section

   Simple markup for :span:{:strong:, :emphas:}
   web native:: scientific publications.

The features illustrated on this page cover 90% of what can be done with RSM.

.. admonition:: Summary

   The base language is comprised of *tags*, which delimit or modify text.  Some tags
   introduce new parts of the manuscript (block tags), while others simply annotate
   their content (inline tags), or modify the enclosing tag (meta tags).  All tags are
   introduced by using their name surrounded by colons ``:tag-name:`` and end at a
   Halmos, or empty tag, ``::``.  Some tags allow for shorthand notation, such as using
   asterisks ``*`` to introduce bold text.  Tags can be nested within the contents of
   other tags.

.. grid:: 1 1 1 2

   .. grid-item::

      .. tip::
         Whitespace is ignored essentially everywhere in RSM.  It is recommended to leave
         generous whitespace where desired to improve readability.

   .. grid-item::

      .. tip::
         Each code block on this site has a button on the bottom right corner that opens
         the code snippet in the online editor.
