.. _guide-structured-proofs:

Structured proofs
=================

In "How to Write a 21st Century Proof" [#lamport]_, Leslie Lamport argues
that a proof written as paragraphs of prose hides its gaps, and proposes
another form: a proof is a list of numbered steps, each step states one claim
and gives its justification, and a step whose justification is not obvious is
itself proved by a list of smaller steps. Writing a proof this way makes it
harder to prove something that is false, and lets the reader read only as
deep as they need.

RSM supports this form of proof directly. The reader of an RSM page can fold
the steps that they trust, open the ones that they doubt, and see which
assumptions are in force at each step.

This page builds one proof, that :math:`\sqrt{2}` is irrational, step by step.
The tags are listed in :ref:`ref-proofs`.


The whole proof
---------------

.. rsm::

   ## Results

   :theorem: {:label: thm-sqrt2}
   $\sqrt{2}$ is irrational.
   ::

   :proof:

     :step: {:label: st-ab} :assume: $\sqrt{2} = a/b$ for whole numbers $a$
     and $b$ with no common factor ::.
     ::

     :step: {:label: st-a} :claim: $a$ is even ::.

       :step: {:label: st-sq} :claim: $a^2 = 2b^2$ ::.

         :p: Square both sides of :ref:st-ab:: and multiply by $b^2$. ::

       ::

       :step: :claim: $a^2$ is even, and so is $a$ ::.

         :p: By :prev:, and because the square of an odd number is odd. ::

       ::

     ::

     :step: :claim: $b$ is even ::.

       :step: :let: $a = 2c$ ::.

         :p: $a$ is even by :ref:st-a::. ::

       ::

       :step: :claim: $b^2 = 2c^2$, so $b$ is even ::.

         :p: Put $a = 2c$ into :ref:st-sq::, which gives $4c^2 = 2b^2$. ::

       ::

     ::

     :step: :qed:

       :p: So 2 divides both $a$ and $b$, which contradicts :ref:st-ab::. ::

     ::

   ::

The rest of this page goes through the parts of this proof.


Write the steps
---------------

Each step is a ``:step:`` block inside the ``:proof:``, and ends with ``::``.
RSM numbers the steps ⟨1⟩, ⟨2⟩, ⟨3⟩ in order.

Start each step with what it states. Mark that statement with a keyword
tag, so that both the reader and RSM know what the step does:

- ``:assume:`` for an assumption, as in step ⟨1⟩,
- ``:let:`` for a new symbol, as in step ⟨3.1⟩,
- ``:claim:`` for what the step asserts, as in step ⟨2⟩.

RSM shows the keyword in the page, such as "ASSUME", "LET" or "⊢". Other
keywords, such as ``:case:`` and ``:suffices:``, are listed in
:ref:`ref-proofs`.


Say why a step holds
--------------------

Put the reason for a step in a ``:p:`` inside it, after its statement. Keep
the claim and its reason apart: the claim says what holds, and the ``:p:``
says why. A reader who accepts the claim can skip the reason.


Break a step into smaller steps
-------------------------------

A step can hold steps of its own, written inside it before its closing
``::``. Step ⟨2⟩ above has two, numbered ⟨2.1⟩ and ⟨2.2⟩. Use sub-steps when
the reason for a claim takes more than one sentence: each sub-step is a
smaller claim that the reader can check, open or fold on its own.


Refer to other steps
--------------------

``:prev:`` links to the step before, at the same level, as in step ⟨2.2⟩.
``:prev2:`` and ``:prev3:`` go two and three steps back.

To refer to any other step, give it a ``:label:`` and use ``:ref:``, as with
any other block. The justification of step ⟨4⟩ refers to step ⟨1⟩ by its
label ``st-ab``.

These links are what the sidebar uses to draw which steps depend on which, so
it pays to write them even when the step that you mean is obvious.


What the reader can do
----------------------

In the built page:

- Each step has a handrail that folds and opens it. A folded step shows only
  its statement.
- Hovering over a reference to a step, or tapping it on a phone, shows that
  step in a tooltip.
- With ``rsm build --sidebar``, the sidebar has a "Proof steps" view, a graph
  of the steps of the proof in view and the results that they use, and a
  "Proof state" view, which lists the assumptions and symbols in force at the
  current step and the claim that it proves. See :ref:`reading-sidebar`.


A sketch next to the proof
--------------------------

To offer a short version of a proof as well as the full one, put a
``:sketch:`` and the ``:proof:`` in two tabs. See :ref:`ref-tabs`.


A chain of equations
--------------------

When a proof is a chain of equalities or inequalities, write it as a
``:calc:``: one ``:step:`` per line, each with its reason in a ``:p:``. See
:ref:`tag-calc`.


.. rubric:: References

.. [#lamport] Leslie Lamport, "How to Write a 21st Century Proof",
   *Journal of Fixed Point Theory and Applications* 11 (2012), 43-63.
   `doi:10.1007/s11784-012-0071-6 <https://doi.org/10.1007/s11784-012-0071-6>`_.
