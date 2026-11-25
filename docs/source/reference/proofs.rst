.. _ref-proofs:

Proofs
======

A proof can be plain text, or a list of numbered steps. Each step states one
thing and can hold its own justification and its own sub-steps. RSM numbers
the steps ⟨1⟩, ⟨2⟩ and, inside step 2, ⟨2.1⟩, ⟨2.2⟩. The reader can fold each
step, and the sidebar shows the steps and what each step depends on. See
:ref:`guide-structured-proofs` for a longer example.

Every tag on this page takes the meta keys that all tags take, such as
``:label:`` and ``:collapsed:``. See :ref:`ref-meta-keys`.


.. _tag-proof:

.. rst-class:: tag-card

Proof ``:proof:``
-----------------

A proof. A proof right after a theorem-like block proves that block. A proof
anywhere else names the block that it proves with ``:of:``, and its heading is
then "Proof of Theorem 1.1", with a link.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :theorem: {:label: <label>}
   <statement>
   ::

   :proof: {:of: <label>}
   <text or steps>
   ::

.. rubric:: Meta keys

``:of:``
   The label of the block that the proof proves.

.. rubric:: Example

.. rsm::

   ## Results

   :theorem: {:label: thm-sq}
   The square of an odd number is odd.
   ::

   We postpone the proof.

   :proof: {:of: thm-sq}
   If $n = 2k + 1$, then $n^2 = 2(2k^2 + 2k) + 1$. :qed:
   ::

.. rubric:: Related

:ref:`Step <tag-step>`, :ref:`Sketch <tag-sketch>`, :ref:`QED <tag-qed>`.


.. _tag-sketch:

.. rst-class:: tag-card

Sketch ``:sketch:``
-------------------

The idea of a proof, in a few sentences, headed "Proof sketch". It goes right
after the block that it is about.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :sketch:
   <text>
   ::

.. rubric:: Related

:ref:`Proof <tag-proof>`.


.. _tag-step:

.. rst-class:: tag-card

Step ``:step:``
---------------

One step of a proof. A step starts with what it states, which can use the
keywords below, such as ``:let:`` and ``:claim:``. Its justification goes in a
``:pf:``, and its sub-steps follow as more ``:step:`` blocks. The step ends with
``::``.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :proof:
     :step: <statement>

       :pf: <justification> ::

     ::
   ::

.. rubric:: Example

.. rsm::

   :proof:

     :step: {:label: st-n} :let: $n = 2k$ ::.
     ::

     :step: :claim: $n^2 = 4k^2$ ::.

       :pf: By :prev:, $n^2 = (2k)^2$. ::

     ::

     :step: So 4 divides $n^2$. :qed:
     ::

   ::

.. rubric:: Related

:ref:`Justification <tag-p>`, :ref:`Proof keywords <tag-claim>`,
:ref:`Step references <tag-prev>`.


.. _tag-p:

.. rst-class:: tag-card

Justification ``:pf:``
----------------------

The reason for a step, inside the step and after its statement. It ends with
``::``.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :proof:
     :step: <statement>

       :pf: <justification> ::

     ::
   ::

.. rubric:: Related

:ref:`Step <tag-step>`.


.. _tag-claim:
.. _tag-assume:
.. _tag-let:

.. rst-class:: tag-card

Proof keywords ``:claim:`` ``:assume:`` ``:let:`` …
---------------------------------------------------

Inline tags that say what part of a step does. RSM shows each one as a
keyword, such as "LET" or "⊢", and the sidebar uses them to show which
assumptions and symbols are in force at each step. Each one ends with ``::``.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :proof:
     :step: :assume: <assumption> ::.
     ::
   ::

.. rubric:: Tags

``:claim:``
   What the step asserts. Shown as "⊢". ``:|-:`` and ``:⊢:`` are the same
   tag.

``:assume:``
   An assumption. Shown as "ASSUME".

``:suppose:``, ``:wlog:``
   Other ways to state an assumption, the second one made without loss of
   generality. Shown as "SUPPOSE" and "WLOG".

``:let:``
   A new symbol and its value or its property. Shown as "LET".

``:define:``, ``:new:``, ``:write:``
   Other ways to bring in a symbol, shown as "DEFINE", "NEW" and "WRITE".

``:pick:``, ``:st:``
   A symbol picked with a property, as in ``:pick: $x$ :: :st: $x > 0$ ::``.
   Shown as "PICK" and "SUCH THAT".

``:case:``
   One case of a proof by cases. Shown as "CASE".

``:then:``
   A consequence. Shown as "THEN".

``:prove:``, ``:suffices:``
   The goal of the step, and a goal that is enough to reach it. Shown as
   "PROVE" and "SUFFICES".

.. rubric:: Related

:ref:`Step <tag-step>`.


.. _tag-qed:

.. rst-class:: tag-card

QED ``:qed:``
-------------

Marks the end of the argument, shown as "QED". It goes in the text of the
last step, or at the end of a proof without steps, and has no closing ``::``.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :proof:
   <text> :qed:
   ::

.. rubric:: Related

:ref:`Proof <tag-proof>`.


.. _tag-prev:
.. _tag-previous:

.. rst-class:: tag-card

Step references ``:prev:`` ``:prev2:`` ``:prev3:`` ``:previous:``
-----------------------------------------------------------------

A link to an earlier step at the same level: the step before this one, two
steps before, three steps before, or the number of steps before given in
``:previous:``. ``:prev:``, ``:prev2:`` and ``:prev3:`` have no closing
``::``. They work only inside a step.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :proof:
     :step: {:label: <label>} <statement>
     ::

     :step: <statement> by :prev: and :previous: 1::.
     ::
   ::

.. rubric:: Related

:ref:`Step <tag-step>`, :ref:`ref-references`.


.. _tag-calc:

.. rst-class:: tag-card

Calculation ``:calc:``
----------------------

A chain of equalities or inequalities, one per line, each with its reason. It
goes wherever displayed math can go. Each line is a ``:step:`` whose
statement is math, with its reason in a ``:pf:``. A calculation with a
``:label:`` is numbered as an equation.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :calc:
     :step: $<left> = <right>$

       :pf: <reason> ::

     ::
   ::

.. rubric:: Example

.. rsm::

   :calc: {:label: calc-sq}

     :step: $(a+b)^2 = (a+b)(a+b)$

       :pf: by definition ::

     ::

     :step: $= a^2 + 2ab + b^2$

       :pf: expand ::

     ::

   ::

   :ref:calc-sq:: has two steps.

.. rubric:: Related

:ref:`Step <tag-step>`, :ref:`ref-math-code`.
