.. _reading-proofs:

Proofs
======

A structured proof is a list of numbered steps, and each step can have a
proof of its own, with steps of its own. A reader can open only the steps
they want to read, see which earlier steps a step uses, and see what is
assumed and what is left to prove at any step. The example below is built
with the sidebar, so all of these can be tried there.

.. rsm::
   :sidebar:
   :height: 640

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


Open and fold steps
-------------------

A step with a proof of its own can be folded, so that only its statement
shows. Open the menu of the step and choose **Collapse**, and **Expand** to
open it again. On a proof, **Collapse all** folds every step that has a proof
of its own, so the proof reads as a list of statements, and **Expand all**
opens them again.

A folded step says how many steps it hides, such as "2 steps hidden".


See what a step uses
--------------------

With the sidebar, the menu of a step has two more items:

**Depends on**
   Lights the steps that this step rests on, and fades the rest of the
   page.

**Used by**
   Marks the steps that rest on this step.

Both can be on at once. A bar at the bottom of the window says how many steps
are marked, and has a button to add the other direction. Press ``Escape``,
click **Clear**, or click outside the marked steps to turn the marks off.
Theorems, lemmas, propositions and corollaries with a label have the same two
items, for the results that they use and that use them.


The proof views in the sidebar
------------------------------

With the sidebar, two views follow the proof that you last clicked in:

**Proof steps**
   A graph of the steps of the proof, with an arrow from each step to the
   steps it uses. The step that you clicked is filled, and the steps it
   depends on are lit. Point at a step to read it, and click it to go there.

**Proof state**
   For the step that you clicked: what is left to **Prove** there, what is
   **Assumed**, and the symbols **In scope**. Each line links to the step or
   section that introduced it.

Click a step in the example above, then open these views from the sidebar.
See :ref:`reading-sidebar`.


Change the order of the steps
-----------------------------

With the sidebar, on a computer, the menu of a proof has **Reorder**. It puts
a handle on each step, to drag the step to another place. The page allows
only orders in which no step comes before a step that it uses: a red line and
a reason, such as "Step 4 uses Step 2", show where a step cannot go. Choose
**Done**, or press ``Escape``, to stop. The new order lasts until the page is
reloaded, and goes with a link made with **Copy a link to this view**.


Calculations
------------

A calculation is a chain of equalities or inequalities, one per line. Each
line has a **∵** mark on the right: click it to show or hide the reason for
that line.
