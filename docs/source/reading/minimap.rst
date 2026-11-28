.. _reading-minimap:

The map of the document
=======================

An RSM page replaces the browser's scroll bar with a map of the document: a
thin strip at the right edge of the window, with a mark for each section and
each figure, and a box over the part of the page that is on screen. The
example below scrolls inside its frame, so its map is at the right edge of
the frame.

.. rsm::
   :height: 420
   :layout: stacked

   # Sums of whole numbers

   ## Even numbers

   A whole number is even when it is twice a whole number, so the even
   numbers are $0, 2, 4, 6$ and so on. Every second number on the number line
   is even.

   Adding two even numbers $2a$ and $2b$ gives $2(a + b)$, which is twice a
   whole number. So the sum of two even numbers is even, and so is the sum of
   any number of even numbers.

   ## Odd numbers

   A whole number is odd when it is one more than an even number, so the odd
   numbers are $1, 3, 5, 7$ and so on. Every whole number is either even or
   odd, and never both.

   Adding two odd numbers $2a + 1$ and $2b + 1$ gives $2(a + b + 1)$, which
   is even. Adding an odd number and an even number gives an odd number.

   ## Products

   The product of an even number and any whole number is even, because one
   of the factors already has a factor of 2. The product of two odd numbers
   is odd.

   So a product is odd only when every factor is odd, and a single even
   factor makes the whole product even.

   ## Squares

   The square of an even number is even, and the square of an odd number is
   odd. So a number and its square are always both even or both odd.

   This is the fact that the proof that $\sqrt{2}$ is irrational uses: if
   $a^2$ is even, then $a$ is even.


With a mouse
------------

- Point near a mark to see the title of its section, or the number of its
  figure.
- Click a mark to go there, or click anywhere else on the strip to jump to
  that part of the page.
- Drag anywhere on the strip to scroll, as with a scroll bar.


With the keyboard
-----------------

The map is one stop of the ``Tab`` key. On the map, the arrow keys move to the
next or the previous mark, ``Home`` and ``End`` to the first and the last,
and ``Enter`` or ``Space`` go to the mark. ``Escape`` goes back to the text.


On a touch screen
-----------------

On a phone, the map shows only while the page scrolls or the strip is
touched. The first tap on a mark shows its title, and a second tap goes
there.


Turn the map off
----------------

A reader can hide the map with the **Map** setting in the Reading view of the
sidebar (see :ref:`reading-sidebar`). The choice applies to every RSM page from
the same website. An author can leave the map out of a document with
``:no-minimap:`` in its ``:config:`` block. Without JavaScript, the page has
the browser's own scroll bar.
