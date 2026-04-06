.. _syntax:

Syntax guide
============

This guide covers the complete RSM syntax. For a quick introduction, see :ref:`markup`.
For practical examples, see :ref:`recipes`.

Base language
*************

The double colon is referred to as `Halmos
<https://en.wikipedia.org/wiki/Tombstone_(typography)>`_. The base language contains one
special character (the colon ``:``), three types of *tags*, and only a handful of syntax
rules.

Tags
----

One of the main goals of RSM is to separate your manuscript's content from the look and
feel. Accordingly, RSM provides *semantic tags* that annotate the contents of your
manuscript. A tag has the form ``:tag-name: <contents> ::``.

Tags being semantic means that a tag determines what its contents *are*, not what they
should look like.  Two parts of your manuscript may be annotated with the same tag but
end up looking differently in the final output.  Later on we will see examples of this.

You can think of the Halmos ``::`` as the *empty* tag.  With few exceptions, every
region of text annotated with a tag always ends with a Halmos.

Types of tags
-------------

There are three different types of tags in RSM: block, inline, and meta.  If you are
familiar with HTML, blocks and inlines work in RSM much the same way as block and inline
elements in HTML, whereas meta tags are similar in some respects to HTML attributes.

Block and inline tags are meant to carry content.  The content may be text or other
tags.  Meta tags are special in that they associate metadata to the immediately
enclosing tag.  Consider this example:

.. rsm::

   :theorem: {
     :title: Fermat's Last Theorem
     :label: thm-fermat
   }

   For integer $n > 2$, the equation
   $x^n + y^n = z^n$ has no positive
   integer solutions.

   ::

Here we have a ``:theorem:`` block tag with two meta tags: ``:title:`` and ``:label:``.
The ``:title:`` meta tag associates the title "Fermat's Last Theorem" to the theorem,
and ``:label:`` provides a unique identifier ``thm-fermat`` that we can use to reference
this theorem later. Meta tags always come in key-value pairs inside braces ``{}``.

In the previous example, the ``:title:`` meta tag had a visible effect on the output
(the theorem title appears), while ``:label:`` has no visible effect but allows us to
reference the theorem elsewhere:

.. rsm::

   :theorem: {
     :label: thm-ref-example
   }
   A theorem we want to reference.
   ::

   As we proved in
   :ref:thm-ref-example::, the result
   follows.

Syntax rules
------------

Tags can be one of two main types: *blocks* or *inlines*.  They are differentiated by
the syntax used to introduce them:

.. grid:: 1 2 2 2

  .. grid-item-card:: Block tags

     .. code-block:: text

        :tag: {
          :key: val
        }

        <content>

        ::

     Example:

     .. rsm::

        :remark:
        A simple remark rendered as a block.
        ::


  .. grid-item-card:: Inline tags

     .. code-block:: text

        :tag: {:key: val} <content> ::

     Example:

     .. rsm::

        Text with :span: {:strong:} bold :: words.

Here the ellipsis denote an arbitrary number of additional key-value pairs.  In general,
blocks introduce a part of the manuscript that should be regarded as completely separate
from all other parts, while inlines denote a region of text that is part of the
enclosing block.

The third type of tag is *meta* tags.  They are the tags used above to modify their
parent tags via key-value pairs. Meta tags appear inside braces ``{}`` and provide
metadata about the enclosing tag. For example:

.. rsm::

   :theorem: {
     :title: Pythagorean Theorem
     :label: pythag
   }

   For a right triangle,
   $a^2 + b^2 = c^2$.

   ::

Here ``:title:`` and ``:label:`` are meta tags that modify the ``:theorem:`` block tag.
The ``:title:`` meta tag determines what title is displayed, while ``:label:`` provides
an identifier for cross-referencing. Some meta tags like ``:label:`` and ``:nonum:``
work with many different tags, while others like ``:path:`` (for figures) are specific
to certain tags.
