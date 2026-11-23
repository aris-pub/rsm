.. _reading-sidebar:

The sidebar
===========

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
