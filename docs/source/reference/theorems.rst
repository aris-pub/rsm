.. _ref-theorems:

Theorem-like blocks
===================

The ten tags on this page share one counter, numbered within each section:
in section 2, a definition, a theorem and a lemma are numbered 2.1, 2.2 and
2.3. In a document without sections, they are numbered 1, 2, 3.

Every tag on this page takes the same meta keys as ``:theorem:``, and the meta
keys that all tags take, such as ``:label:``, ``:nonum:`` and ``:collapsed:``.
See :ref:`ref-meta-keys`.


.. _tag-theorem:

.. rst-class:: tag-card

Theorem ``:theorem:``
---------------------

A theorem. The block starts with the tag and ends with ``::``, and can hold
paragraphs, lists, math and other blocks.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :theorem: {:label: <label>, :title: <title>}
   <statement>
   ::

.. rubric:: Meta keys

``:title:``
   A name for the theorem, shown after its number. It can hold inline markup,
   such as math.

``:blockname:``
   A name that replaces "Theorem" in the label and in references to the
   block, such as ``Conjecture``. It can hold inline markup, such as math.

.. rubric:: Example

.. rsm::

   ## Results

   :theorem: {:label: thm-sum, :title: Sum of evens}
   The sum of two even numbers is even.
   ::

   :lemma: {:blockname: Claim}
   Every even number is $2k$ for a whole number $k$.
   ::

   :ref:thm-sum:: uses the claim.

.. rubric:: Related

:ref:`Lemma <tag-lemma>`, :ref:`Definition <tag-definition>`,
:ref:`Proofs <ref-proofs>`.


.. _tag-lemma:

.. rst-class:: tag-card

Lemma ``:lemma:``
-----------------

A result that is used to prove another one. It works as ``:theorem:`` does, and is labelled "Lemma".

.. rubric:: Syntax

.. rsm::
   :source-only:

   :lemma: {:label: <label>, :title: <title>}
   <text>
   ::

.. rubric:: Related

:ref:`Theorem <tag-theorem>`.


.. _tag-proposition:

.. rst-class:: tag-card

Proposition ``:proposition:``
-----------------------------

A result, usually less central than a theorem. It works as ``:theorem:`` does, and is labelled "Proposition".

.. rubric:: Syntax

.. rsm::
   :source-only:

   :proposition: {:label: <label>, :title: <title>}
   <text>
   ::

.. rubric:: Related

:ref:`Theorem <tag-theorem>`.


.. _tag-corollary:

.. rst-class:: tag-card

Corollary ``:corollary:``
-------------------------

A result that follows from another one. It works as ``:theorem:`` does, and is labelled "Corollary".

.. rubric:: Syntax

.. rsm::
   :source-only:

   :corollary: {:label: <label>, :title: <title>}
   <text>
   ::

.. rubric:: Related

:ref:`Theorem <tag-theorem>`.


.. _tag-definition:

.. rst-class:: tag-card

Definition ``:definition:``
---------------------------

The definition of a term or an object. It works as ``:theorem:`` does, and is labelled "Definition".

.. rubric:: Syntax

.. rsm::
   :source-only:

   :definition: {:label: <label>, :title: <title>}
   <text>
   ::

.. rubric:: Related

:ref:`Theorem <tag-theorem>`.


.. _tag-remark:

.. rst-class:: tag-card

Remark ``:remark:``
-------------------

A comment on the text around it. It works as ``:theorem:`` does, and is labelled "Remark".

.. rubric:: Syntax

.. rsm::
   :source-only:

   :remark: {:label: <label>, :title: <title>}
   <text>
   ::

.. rubric:: Related

:ref:`Theorem <tag-theorem>`.


.. _tag-example:

.. rst-class:: tag-card

Example ``:example:``
---------------------

An example. It works as ``:theorem:`` does, and is labelled "Example".

.. rubric:: Syntax

.. rsm::
   :source-only:

   :example: {:label: <label>, :title: <title>}
   <text>
   ::

.. rubric:: Related

:ref:`Theorem <tag-theorem>`.


.. _tag-exercise:

.. rst-class:: tag-card

Exercise ``:exercise:``
-----------------------

An exercise for the reader. It works as ``:theorem:`` does, and is labelled "Exercise".

.. rubric:: Syntax

.. rsm::
   :source-only:

   :exercise: {:label: <label>, :title: <title>}
   <text>
   ::

.. rubric:: Related

:ref:`Theorem <tag-theorem>`.


.. _tag-problem:

.. rst-class:: tag-card

Problem ``:problem:``
---------------------

A problem for the reader. It works as ``:theorem:`` does, and is labelled "Problem".

.. rubric:: Syntax

.. rsm::
   :source-only:

   :problem: {:label: <label>, :title: <title>}
   <text>
   ::

.. rubric:: Related

:ref:`Theorem <tag-theorem>`.


.. _tag-porism:

.. rst-class:: tag-card

Porism ``:porism:``
-------------------

A result that comes out of the proof of another one. It works as ``:theorem:`` does, and is labelled "Porism".

.. rubric:: Syntax

.. rsm::
   :source-only:

   :porism: {:label: <label>, :title: <title>}
   <text>
   ::

.. rubric:: Related

:ref:`Theorem <tag-theorem>`.
