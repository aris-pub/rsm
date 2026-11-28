.. _explanation-structured-proofs:

Structured proofs
=================

RSM writes proofs as structured proofs, a form that Leslie Lamport proposed
in "How to Write a Proof" (*The American Mathematical Monthly*, 1995) and
again in "How to Write a 21st Century Proof" (*Journal of Fixed Point
Theory and Applications*, 2012). This page explains the idea, and what it
gives the author and the reader of an RSM page.


The idea
--------

A proof in prose is a run of paragraphs. The reader has to find where each
claim starts and ends, which earlier claims it uses, and what is assumed at
that point. In a long proof, it is easy to lose that thread, for the reader
and for the author.

A structured proof is a list of numbered steps instead. Each step states one
claim, and comes with its own proof. That proof is either a short
justification or a list of steps of its own, and so on, down to steps that
are simple enough to justify in a sentence. A proof is then a tree of claims:
the top level gives the whole argument in a few lines, and each level below
gives the details of one step.

The steps say what they do. A step can assume something for the rest of its
proof, introduce a name, split into cases, or reduce what is left to prove to
something simpler. Lamport wrote these as keywords, and RSM has them as
tags: ``:assume:``, ``:let:``, ``:case:``, ``:suffices:`` and the others (see
:ref:`ref-proofs`). Each step can cite the earlier steps that it uses, by
their numbers.


What it gives the author
------------------------

Writing each claim as a step makes every gap visible: a step whose proof does
not follow from what is cited is easy to spot, because the claim and the
reasons sit next to each other.

The steps are also easy to change. A step can be moved, split or proved in
more detail without rewriting the paragraphs around it.


What it gives the reader
------------------------

A reader can read a structured proof at the level of detail that they want.
On an RSM page this is more than a way of writing: because RSM knows the
steps and what each one cites, the page can show the structure.

- The reader folds the proof down to its top level and opens only the steps
  that they want to check.
- **Depends on** and **Used by** show which steps a step rests on, and which
  rest on it.
- The **Proof state** view shows what is assumed and what is left to prove
  at any step.
- The **Proof steps** view draws the steps and the steps they use as a graph.

See :ref:`reading-proofs` for all of them, and :ref:`guide-structured-proofs`
for how to write a structured proof in RSM.


Prose proofs still have their place
-----------------------------------

A short proof that reads well as a paragraph does not need steps, and RSM
writes it as a paragraph inside ``:proof:``. A ``:sketch:`` gives the idea of
a proof in a few sentences. Structured proofs are for proofs that are
long enough, or subtle enough, to lose the reader in prose.
