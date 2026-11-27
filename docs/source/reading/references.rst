.. _reading-references:

References, footnotes and asides
================================

A reference in the text, such as "Theorem 1.1" or "(2.3)", is a link. A
reader can read what it points to without leaving their place, or follow it
and come back.

.. rsm::

   ## Sums {:label: sec-sums}

   :theorem: {:label: thm-even}
   The sum of two even numbers is even.
   ::

   $$ {:label: eq-sum}
   2a + 2b = 2(a + b).
   $$

   By :ref:eq-sum::, :ref:thm-even:: holds :note:fn-def::. Odd numbers
   behave :aside:odd,differently::, as :cite:knuth:: notes.

   :note: {:label: fn-def} A number is even when 2 divides it. ::

   :aside: {:label: odd} The sum of two odd numbers is even too. ::

   :references:
   @book{knuth,
     author = {Knuth, Donald E.},
     title = {The Art of Computer Programming},
     year = {1997},
     publisher = {Addison-Wesley}
   }
   ::


Read a reference in a tooltip
-----------------------------

Point at a reference to see what it points to in a tooltip. Move the pointer
into the tooltip to read all of it, and away to close it. The tooltip shows:

- for a theorem, a lemma, a definition, an equation or a paragraph: the whole
  block,
- for a proof: the whole proof, with its steps open,
- for a step of a proof: its statement,
- for a section: its heading and its first block,
- for a figure: the image and the caption. An interactive figure shows its
  image, or a description of it, and says that it is interactive in the page,
- for a citation: the entry of the bibliography,
- for a footnote: the text of the note.

On a touch screen, the first tap on a reference shows the tooltip, and a
second tap follows the link. A tap anywhere else closes the tooltip.


Follow a reference and come back
--------------------------------

Click a reference to go to what it points to. When the target is inside a
folded block or a tab that is not shown, the page opens the block or the tab.

After the jump, a **← Back** button shows at the bottom of the window. Click
it to go back to where you were. The button goes away after a few seconds, or
when you scroll away. The browser's own Back button does the same.


Footnotes
---------

A footnote shows as a small number in the text. Point at it to read the note,
or click it to go to the list of notes at the end of the document. Each note
in the list has a **↖** link that goes back to the text.


Citations
---------

A citation shows the number of the entry in the bibliography. Point at it to
read the entry, or click it to go there. In the bibliography, an entry with a
DOI or a web address has a **DOI ↗** or **Link ↗** link, and a **cited ↖**
link back to each place that cites it. These links show when the pointer is
over the entry, and all the time on a touch screen.


Asides
------

An aside is a short remark about a phrase, which is underlined with dots.

- When the window is wide enough, asides sit in the margin, next to their
  phrase.
- Otherwise, an aside is hidden. Point at its phrase to read it in a tooltip,
  or click the phrase to open the aside below the paragraph, and click it
  again to close it.

Pointing at the phrase or at the aside tints both, so that it is clear which
phrase an aside is about.


The margin
----------

When the window is wide enough, a column on the right of the text holds the
asides and the captions of figures, tables and code, next to their block. On a
narrower window, captions go back under their block and asides open below
their paragraph. The margin shows only on pages that have an aside or a
caption.
