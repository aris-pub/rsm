.. _markup:

Readable Science Markup
=======================

Readable Science Markup (RSM) is a markup language for writing web-first scientific
manuscripts. It combines the simplicity of Markdown with the power of semantic tagging.

.. rsm::

    # Getting Started with RSM

    :author: {
      :name: RSM Team
      :affiliation: The Aris Program
    } ::

    ## Introduction
    RSM was inspired by popular languages such
    as Markdown, ReST, and LaTeX. RSM strives
    for simplicity, flexibility, and
    functionality.

The main syntax feature of RSM are *tags*. Strings such as ``:author:`` and ``:name:``
are called *tags*. In RSM, tags are are both a syntactic element, i.e. they act as
delimiters for regions of text, and a semantic element, i.e. they annotate text based on
meaning, not just structure.

.. rsm::

   :abstract:
   This is the manuscript's abstract.
   ::

The ``:abstract:`` tag is a *block* tag that introduces a clearly separated part of the
manuscript. Some tags can also have meta-data attached. For example, the ``:author:``
tag in the first example uses ``:name:`` and ``:affiliation:`` tags to specify author
details. Tags like ``:name:`` and ``:affiliation:`` are called *meta* tags. They appear
inside braces ``{}`` immediately after the opening tag and modify their parent tag.

Tags such as ``:author:`` and ``:abstract:`` introduce parts of the manuscript that are
clearly separated from other parts. These are called *block* tags. In contrast, the
following example illustrates the ``:span:`` tag.

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
*shorthand* notation using asterisks (``*``).

.. rsm::

   Span tags do not introduce new parts, but
   **live within** their parents.

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

.. admonition:: Summary

   The base language is comprised of *tags*, which delimit or modify text.  Some tags
   introduce new parts of the manuscript (block tags), while others simply annotate
   their content (inline tags), or modify the enclosing tag (meta tags).  All tags are
   introduced by using their name surrounded by colons ``:tag-name:`` and end at a
   Halmos, or empty tag, ``::``.  Some tags allow for shorthand notation, such as using
   asterisks ``*`` to introduce bold text.  Tags can be nested within the contents of
   other tags.

.. tip::
   Whitespace is ignored essentially everywhere in RSM.  It is recommended to leave
   generous whitespace where desired to improve readability.
