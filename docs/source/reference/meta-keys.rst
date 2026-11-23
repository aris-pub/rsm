.. _ref-meta-keys:

Meta keys
=========

Meta keys add information to a tag. They go in braces right after the tag,
separated by commas or on lines of their own. A key with a value is written
``:key: value``, and a key without a value, such as ``:nonum:``, is on or off.

.. rsm::
   :source-only:

   :theorem: {:label: thm-main, :title: Main result, :nonum:}
   <statement>
   ::

A key that RSM does not know is ignored, with a warning.


.. _keys-common:

.. rst-class:: tag-card

Keys of every tag
-----------------

Every tag takes these keys. A key that has no use for a tag, such as
``:nonum:`` on a tag that is not numbered, has no effect.

.. rubric:: Meta keys

``:label:``
   A name for the block, so that ``:ref:`` can link to it. A label is one
   word of letters, digits and hyphens, used only once in the document.

``:nonum:``
   Leaves the block unnumbered.

``:class:``
   One or more CSS classes, separated by commas. See :ref:`styling`.

``:collapsed:``
   Starts the block folded. The reader opens it with its handrail.

``:reftext:``
   Text that replaces the kind and number in every reference to the block,
   such as "the main lemma".

.. rubric:: Example

.. rsm::

   ## Results

   :lemma: {:label: lem-main, :reftext: the main lemma}
   Every even number is $2k$ for a whole number $k$.
   ::

   We use :ref:lem-main:: twice.

.. rubric:: Related

:ref:`Reference <tag-ref>`.


.. _keys-index:

All meta keys
-------------

Each key, and where it is described.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Key
     - Described in
   * - ``:label:``, ``:nonum:``, ``:class:``, ``:collapsed:``, ``:reftext:``
     - :ref:`Keys of every tag <keys-common>`
   * - ``:title:``
     - :ref:`Theorem <tag-theorem>`, :ref:`Section tags <tag-section>`,
       :ref:`Paragraph <tag-paragraph>`, :ref:`Tabs <tag-tabs>`
   * - ``:blockname:``
     - :ref:`Theorem <tag-theorem>`, :ref:`Figure <tag-figure>`,
       :ref:`Table <tag-table>`
   * - ``:of:``
     - :ref:`Proof <tag-proof>`
   * - ``:path:``, ``:alt:``, ``:static:``, ``:dark:``, ``:scale:``,
       ``:as-paragraph:``
     - :ref:`Figure <tag-figure>`, :ref:`Video <tag-video>`
   * - ``:alt:``
     - :ref:`Raw HTML <tag-html>`
   * - ``:preamble:``, ``:isclaim:``
     - :ref:`Displayed math <tag-mathblock>`
   * - ``:lang:``
     - :ref:`Inline code <tag-code>`, :ref:`Code block <tag-codeblock>`,
       :ref:`Document settings <tag-config>`
   * - ``:strong:``, ``:emphas:``
     - :ref:`Span <tag-span>`
   * - ``:view:``, ``:orientation:``
     - :ref:`Table of contents <tag-toc>`
   * - ``:name:``, ``:affiliation:``, ``:email:``, ``:orcid:``,
       ``:author-note:``
     - :ref:`Author <tag-author>`
   * - ``:keywords:``, ``:msc:``
     - :ref:`Abstract <tag-abstract>`
   * - ``:accent:``, ``:typography:``, ``:numbering:``,
       ``:citation-style:``, ``:override-date:``, ``:eyebrow:``,
       ``:plain-title:``
     - :ref:`Document settings <tag-config>`
