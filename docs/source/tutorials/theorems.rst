.. _tutorial-theorems:

Theorems and proofs
===================

Mathematical writing is made of theorems, definitions, proofs and similar
blocks. RSM has a tag for each of them, and numbers and links them for you.

.. rsm::

   # Even numbers

   ## Sums

   :definition: {:label: def-even}
   A whole number $n$ is **even** if $n = 2k$ for some whole number $k$.
   ::

   :theorem: {:label: thm-sum, :title: Sum of evens}
   The sum of two even numbers is even.
   ::

   :proof:
   Let $m = 2a$ and $n = 2b$. Then $m + n = 2(a + b)$, which is even
   by :ref:def-even::.
   ::

   :remark: {:nonum:}
   The same argument proves that the product of two even numbers is even.
   ::

   :corollary:
   The sum of any finite list of even numbers is even, by induction and
   :ref:thm-sum::.
   ::


Theorem-like blocks
-------------------

A theorem-like block starts with its tag and ends with ``::``. RSM has these
tags for theorem-like blocks:

``:theorem:``, ``:lemma:``, ``:proposition:``, ``:corollary:``,
``:definition:``, ``:remark:``, ``:example:``, ``:exercise:``, ``:problem:``
and ``:porism:``.

They share one counter within each section, so the definition, theorem and
corollary above are 1.1, 1.2 and 1.3.

Meta keys go in braces right after the tag, separated by commas:

- ``:label:`` names the block, so that ``:ref:`` can link to it.
- ``:title:`` gives it a name, printed after its number.
- ``:nonum:`` leaves it unnumbered.


Proofs
------

``:proof:`` holds a proof, and ``::`` ends it. A proof that comes right after
its theorem needs nothing else. A proof placed somewhere else names its
theorem with ``:of:``:

.. rsm::

   # Odd numbers

   ## Odd squares

   :theorem: {:label: thm-odd}
   The square of an odd number is odd.
   ::

   We postpone the proof.

   :proof: {:of: thm-odd}
   If $n = 2k + 1$, then $n^2 = 2(2k^2 + 2k) + 1$.
   ::

The proof's heading is then "Proof of Theorem 1.1", with a link to the
theorem.

RSM can also split a proof into numbered steps, each with its own claim and
its own justification, and it draws the dependencies between steps for the
reader. See :ref:`guide-structured-proofs`.

The next lesson is :ref:`tutorial-references`.
