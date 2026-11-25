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
   :sidebar:

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

         :pf: Square both sides of :ref:st-ab:: and multiply by $b^2$. ::

       ::

       :step: :claim: $a^2$ is even, and so is $a$ ::.

         :pf: By :prev:, and because the square of an odd number is odd. ::

       ::

     ::

     :step: :claim: $b$ is even ::.

       :step: :let: $a = 2c$ ::.

         :pf: $a$ is even by :ref:st-a::. ::

       ::

       :step: :claim: $b^2 = 2c^2$, so $b$ is even ::.

         :pf: Put $a = 2c$ into :ref:st-sq::, which gives $4c^2 = 2b^2$. ::

       ::

     ::

     :step: :qed:

       :pf: So 2 divides both $a$ and $b$, which contradicts :ref:st-ab::. ::

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

Put the reason for a step in a ``:pf:`` inside it, after its statement.
``:pf:`` stands for "sub-proof": the proof of that one step. Keep
the claim and its reason apart: the claim says what holds, and the ``:pf:``
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
  of the steps of a proof and the results that they use, and a "Proof state"
  view, which lists the assumptions and symbols in force at a step and the
  claim that it proves. On a wide screen, each view has its own icon in the
  strip on the left. On a narrow screen, they are the "Steps" and "State" tabs
  of the "Proof" sheet. See :ref:`reading-sidebar`.

The example at the top of this page is built with the sidebar. Click a step
of the proof, and open "Proof steps" or "Proof state".


A sketch of the proof
---------------------

A ``:sketch:`` gives the idea of a proof in a few sentences, headed "Proof
sketch". It can stand on its own, after its theorem, in place of a proof:

.. rsm::

   :theorem:
   $\sqrt{2}$ is irrational.
   ::

   :sketch:
   If $\sqrt{2} = a/b$ with no common factor, then $a^2 = 2b^2$, so $a$ is
   even, and then so is $b$, which is a contradiction.
   ::

A sketch can also come before the full proof, for readers who want the idea
first. The proof then names its theorem with ``:of:``, since it no longer
comes right after it:

.. rsm::

   :theorem: {:label: thm-sq}
   The square of an odd number is odd.
   ::

   :sketch:
   Expand $(2k + 1)^2$.
   ::

   :proof: {:of: thm-sq}

     :step: {:label: st-n} :let: $n = 2k + 1$ ::.
     ::

     :step: :qed:

       :pf: By :prev:, $n^2 = 2(2k^2 + 2k) + 1$, which is odd. ::

     ::

   ::

If you prefer, you can also put the sketch and the proof in two tabs, so that
the reader sees one at a time. See :ref:`ref-tabs`.


A chain of equations
--------------------

When a proof is a chain of equalities or inequalities, write it as a
``:calc:``: one ``:step:`` per line, each with its reason in a ``:pf:``. The
page shows the lines one under the other, each with a "∵" ("because") sign on
its right; clicking the sign shows the reason for that line. This chain is the
computation inside step ⟨3.2⟩ of the proof above:

.. rsm::

   :calc:

     :step: $2b^2 = a^2$

       :pf: square $\sqrt{2} = a/b$. ::

     ::

     :step: $= (2c)^2$

       :pf: since $a = 2c$. ::

     ::

     :step: $= 4c^2$

       :pf: expand. ::

     ::

   ::

See :ref:`tag-calc`.


.. rubric:: References

.. [#lamport] Leslie Lamport, "How to Write a 21st Century Proof",
   *Journal of Fixed Point Theory and Applications* 11 (2012), 43-63.
   `doi:10.1007/s11784-012-0071-6 <https://doi.org/10.1007/s11784-012-0071-6>`_.
