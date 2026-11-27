.. _reading-blocks:

Blocks and their menus
======================

An RSM page is made of blocks: the title, the sections, the theorems, the
proofs, the paragraphs, the equations and the figures. Point at a block to
see its handrail, the thin line on its left. Try it on the example below.

.. rsm::

   # A short note

   ## Sums {:label: sec-sums}

   :theorem: {:label: thm-even, :title: Even sums}
   The sum of two even numbers is even.
   ::

   :proof:
   Write the numbers as $2a$ and $2b$. Their sum is $2(a + b)$.
   ::

   The proof of :ref:thm-even:: uses only the definition of an even number.


The handrail
------------

When the pointer is over a block, its handrail shows two controls:

- the **arrow**, on the left, which folds and opens the block,
- the **dots** (⋮), which open the menu of the block.

Sections, the title, the abstract, theorems and the other theorem-like
blocks, proofs and sketches have the arrow. Paragraphs, equations, figures and
code have the dots only.

A click on a block selects it, and the block is tinted. A selected block is
where the keyboard shortcuts act: see :ref:`reading-keyboard`.


Fold and open a block
---------------------

Click the arrow to fold a block, and click it again to open it. A folded
block keeps its first line, such as "Theorem 1.1" or the title of a section,
and its handrail shows at rest, with a rounded foot at the bottom. A folded
section hides everything up to the next section.

A folded proof shows how much it hides, such as "3 steps hidden", under its
heading.

The page remembers which blocks you folded and opened, and shows them the
same way the next time you open it in the same browser. The author can also
mark a block to start folded.


The menu
--------

Click the dots to open the menu of a block, and click them again, or move the
pointer away, to close it. The first line of the menu names the block, such
as "Theorem 1.1". The items depend on the kind of block:

**Copy link**
   Copies a link to the block. Anyone who opens the link goes straight to it.
   A block without a label has no address of its own, so the item is shown
   but cannot be chosen.

**Source**
   Opens the RSM source of the block, with a button to copy it.

**Collapse all** and **Expand all**
   On a proof: folds or opens every step of the proof. See
   :ref:`reading-proofs`.

**Static** and **Interactive**
   On an interactive figure: shows the image of the figure instead, and back.

**View as tree** and **View as list**
   On a table of contents: shows the sections as a graph or as a list.

**Pin** and **Unpin**
   With the sidebar: keeps a copy of the block in the sidebar. See
   :ref:`reading-sidebar`.

Proofs have more items, described in :ref:`reading-proofs`.


On a touch screen
-----------------

On a phone or a tablet, which has no pointer to hover with, the handrails
change:

- the dots show on every block all the time, with a larger area to tap,
- the arrow is gone, and the menu has **Collapse** and **Expand** in its
  place,
- the menu opens to the right of the dots.


The authors
-----------

When the list of authors has more than names, it starts folded: the names,
and a line at the foot of the block that counts the affiliations, emails,
ORCID iDs and notes. Click the arrow, the line or the "N more" button to open
it, and the arrow or "Show fewer" to fold it again. Point at a name, or tap
it, to see that author's affiliation and note. See
:ref:`multi-author-guide`.


Without JavaScript and in print
-------------------------------

Without JavaScript, every block is open, and the handrails do nothing.
Printing opens every block and leaves out the handrails and the other
controls.
