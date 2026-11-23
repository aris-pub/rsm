.. _reading-basics:

Tooltips, handrails and the keyboard
====================================

Tooltips
--------

Hover over a reference or a citation, or tap it on a phone, to see what it
points to in a tooltip: the theorem, the equation, the section or the entry
in the list of references. Clicking a reference goes to its target, and a
"Back" button at the bottom of the window then returns to the place that the
reader left.

A tooltip has a pin button, which keeps the block open in the sidebar.


Try them in this example: hover over "Theorem 1.1" in the last line, and move
the pointer over a block to see its handrail.

.. rsm::

   ## Results

   :definition: {:label: def-even}
   A whole number $n$ is **even** if $n = 2k$ for a whole number $k$.
   ::

   :theorem: {:label: thm-sum}
   The sum of two even numbers is even.
   ::

   :proof:
   Let $m = 2a$ and $n = 2b$. Then $m + n = 2(a + b)$, which is even by
   :ref:def-even::. :qed:
   ::

   We use :ref:thm-sum:: below.


Handrails
---------

Each block, such as a paragraph, a theorem or a proof step, has a handrail: a
thin line along its left side. On a computer, the handrail shows when the
pointer is over the block. It has two controls:

- an arrow that folds the block and opens it again,
- three dots that open the block's menu.

On a phone, the three dots show on every block, and folding is in the menu.

The menu holds the actions that make sense for the block:

``Collapse``, ``Collapse all``
   Fold the block, or fold every step inside it.

``Pin``
   Keep the block open in the sidebar while reading elsewhere.

``Copy link``
   Copy a link to the block.

``Source``
   Show the RSM source of the block.

``Static``
   Switch an interactive figure to its still image, and back.

``View as tree``
   Show a table of contents as a graph of which sections refer to which.

``Reorder``
   Drag the steps of a proof into another order, as long as each step still
   comes after the steps that it uses. On a computer only.

``Focus this step``
   Fold every step of the proof except this one and the steps that it uses.

``Depends on``, ``Used by``
   Mark the steps and results that this one rests on, or the ones that rest
   on it.


The margin
----------

On a wide screen, the page has a margin column on the right. The captions of
figures and tables sit there, level with their block, and so do asides. On a
narrow screen, captions sit under their block, and an aside opens under its
block when the reader taps its phrase.


The keyboard
------------

Single keys move around the page and act on the block in focus:

``j``, ``k``
   The next or the previous block.

``H``
   The first block of the page.

``.``
   Open or close the block's menu. In the menu, the arrow keys move and Enter
   acts.

``,``
   Fold or open the block.

``;``
   Fold or open every step inside the block.

``i``
   Show or hide the tooltip of the reference in focus.

``z``
   Scroll the block to the middle of the window.

``Escape``
   Close the menu.
