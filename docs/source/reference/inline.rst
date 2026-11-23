.. _ref-inline:

Inline markup
=============

Markup inside a line of text: bold and italic, spans with meta keys,
footnotes, asides, notes for the authors, raw HTML and comments.


.. _tag-strong:

.. rst-class:: tag-card

Bold and italic ``**`` ``*``
----------------------------

``**...**`` makes text bold, and ``*...*`` makes it italic.

.. rubric:: Syntax

.. rsm::
   :source-only:

   Text with **<bold>** and *<italic>* words.

.. rubric:: Related

:ref:`Span <tag-span>`.


.. _tag-span:

.. rst-class:: tag-card

Span ``:span:``
---------------

A piece of text with meta keys, such as a class for custom styles.

.. rubric:: Syntax

.. rsm::
   :source-only:

   Text with :span: {:class: <class>} <words> :: in it.

.. rubric:: Meta keys

``:strong:``
   Makes the text bold, as ``**`` does.

``:emphas:``
   Makes the text italic, as ``*`` does.

``:class:``
   One or more CSS classes, separated by commas. See :ref:`styling`.

.. rubric:: Related

:ref:`Bold and italic <tag-strong>`.


.. _tag-note:

.. rst-class:: tag-card

Footnote ``:note:``
-------------------

A footnote, written in two parts. The call ``:note:<label>::`` goes in the
text, after a space, and shows a number. The definition is a
``:note:`` block with the same label, anywhere in the document. Footnotes are
numbered 1, 2, 3 in the order of their calls, and listed at the end of the
document, each with a link back to its call.

.. rubric:: Syntax

.. rsm::
   :source-only:

   A claim :note:<label>::.

   :note: {:label: <label>} <footnote text> ::

.. rubric:: Example

.. rsm::

   The bound is sharp :note:fn-sharp::.

   :note: {:label: fn-sharp} Equality holds for the complete graph. ::

.. rubric:: Related

:ref:`Aside <tag-aside>`.


.. _tag-aside:

.. rst-class:: tag-card

Aside ``:aside:``
-----------------

A note about a phrase of the text, with no number. The call
``:aside:<label>,<phrase>::`` marks the phrase, and the definition is an
``:aside:`` block with the same label. When the page has a margin column, the
aside sits in the margin, level with its phrase. Otherwise the reader opens it
by clicking or tapping the phrase. The phrase can hold inline markup and math.

.. rubric:: Syntax

.. rsm::
   :source-only:

   We map into :aside:<label>,<phrase>:: here.

   :aside: {:label: <label>} <aside text> ::

.. rubric:: Example

.. rsm::

   We map into :aside:hilbert,a Hilbert space:: where the norm is defined.

   :aside: {:label: hilbert} A complete space with an inner product. ::

.. rubric:: Related

:ref:`Footnote <tag-note>`.


.. _tag-draft:

.. rst-class:: tag-card

Draft note ``:draft:``
----------------------

A note for the authors, shown in square brackets in the accent color.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :draft: <note> ::


.. _tag-html:
.. _tag-htmlblock:

.. rst-class:: tag-card

Raw HTML ``:html:`` ``:htmlblock:``
-----------------------------------

HTML written into the page as it is: ``:html:`` inside a line of text, and
``:htmlblock:`` as a block of its own. Where HTML cannot be shown, such as in
tooltips and in files exported to PDF or LaTeX, RSM shows the text in
``:alt:`` instead. An ``:htmlblock:`` can also go inside a ``:figure:``.

.. rubric:: Syntax

.. rsm::
   :source-only:

   Text with :html: {:alt: <text>} <b>HTML</b> :: in it.

   :htmlblock: {:alt: <text>}
   <div>HTML</div>
   ::

.. rubric:: Meta keys

``:alt:``
   The text shown where the HTML cannot be.

.. rubric:: Related

:ref:`Figure <tag-figure>`, :ref:`guide-interactive-figures`.


.. _tag-comment:

.. rst-class:: tag-card

Comment ``%``
-------------

``%`` starts a comment, which runs to the end of the line. RSM leaves it out
of the page. To write a percent sign, write ``\%``.

.. rubric:: Syntax

.. rsm::
   :source-only:

   % <comment>
   Text. % <comment>
