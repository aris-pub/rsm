.. _reading:

Reading an RSM page
===================

An RSM page reads like a paper, and the reader can also look up references
without losing their place, fold and open parts of it, follow how a proof
fits together, and set the type to suit them. This page lists what a reader
can do. The examples on this site are RSM pages, so each feature can be tried
there.


Tooltips
--------

Hover over a reference or a citation, or tap it on a phone, to see what it
points to in a tooltip: the theorem, the equation, the section or the entry
in the list of references. Clicking a reference goes to its target, and a
"Back" button at the bottom of the window then returns to the place that the
reader left.

A tooltip has a pin button, which keeps the block open in the sidebar.


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


.. _reading-sidebar:

The sidebar
-----------

A page built with ``rsm build --sidebar`` has a sidebar. On a computer, it is
a strip of icons on the left, and each icon opens a panel beside the text. On
a phone, it is a bar at the bottom of the screen, and each button opens a
sheet.

``Contents``
   The sections of the document, as a list or as a graph of which sections
   refer to which.

``Notation``
   The symbols declared in the document's ``:notation:``. The reader can
   change how each one is shown, and every equation follows.

``Proof steps``
   A graph of the steps of the proof in view and the results that they use.
   It follows the proof that the reader is reading.

``Proof state``
   For the step in view, the assumptions and symbols in force and the claim
   that it proves.

``Pinned``
   The blocks that the reader has pinned.

``Reading``
   The typeface, size, line height and width of the text, and light or dark
   mode.

The sidebar also has "Copy this view", which copies a link that opens the
page as the reader has set it up: what is folded, the order of the steps, the
notation, the pinned blocks and the place on the page.

The example below is built with the sidebar. Open its views from the strip of
icons on the left of the result.

.. rsm::
   :sidebar:
   :layout: stacked

   # Even squares

   :notation:
     \sq $n^2$ square of n
   ::

   ## Definitions {:label: sec-def}

   :definition: {:label: def-even}
   A whole number $n$ is **even** if $n = 2k$ for a whole number $k$.
   ::

   ## Results

   :theorem: {:label: thm-sq}
   If $n$ is even, then $4$ divides $\sq$.
   ::

   :proof:

     :step: {:label: st-let} :let: $n = 2k$ ::.

       :p: By :ref:def-even::. ::

     ::

     :step: :claim: $\sq = 4k^2$ ::.

       :p: Square both sides of :prev:. ::

     ::

     :step: So $4$ divides $\sq$. :qed:
     ::

   ::


The scroll bar
--------------

The scroll bar on the right is also a map of the page, with a mark for each
section and figure. Hover over a mark to see its name, and click it to go
there.


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
