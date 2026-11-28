.. _reading-sidebar:

The sidebar
===========

A page built with ``rsm build --sidebar`` has a sidebar with the table of
contents, the notation, the proof views, the pinned blocks and the reading
settings.

On a wide window, the sidebar is a column of icons on the left. Click an icon
to open its view in a panel, and click it again, or press ``Escape``, to
close it. The text moves to the right to make room, and the part you were
reading stays in place.

On a phone, the sidebar is a bar at the bottom of the screen, with the
buttons **Document**, **Proof**, **Pinned**, **Reading** and **Copy link**. A
button opens its view in a sheet above the bar. **Document** has two tabs,
**Contents** and **Notation**, and **Proof** has two, **Steps** and
**State**.

The page remembers which view you opened last. The panel always starts
closed.


Contents
--------

The sections of the document, as a list or as a graph. Switch between the
two with the buttons next to the title of the view. In the graph, point at a
section to light the sections that it depends on and to read its beginning
in a tooltip, and click it to go there.


Notation
--------

When the author declares the symbols of the document, this view lists them.
Change how a symbol is written, and the change applies everywhere in the
document:

.. rsm::
   :sidebar:
   :height: 420

   :notation:
     \eig $\lambda$ eigenvalue
   ::

   ## Spectra

   Every $\eig$ of a symmetric matrix is real, and each $\eig$ has an
   eigenvector.

Each symbol has a field with its LaTeX, a **Rename** button, a button that
scrolls to the nearest place where the symbol is used, and **↺** to go back
to the author's choice. A change applies when you press ``Enter`` or leave the
field, and every use of the symbol flashes. Click a symbol in the text to open
this view at that symbol. The page remembers your changes.


Proof steps and Proof state
---------------------------

The graph of the steps of a proof, and what is assumed and left to prove at
a step. See :ref:`reading-proofs`.


Pinned
------

Pin a block to keep a copy of it in this view while you read the rest of the
document, such as a definition that a proof keeps using. Pin a block from its
menu (**Pin**), or with the pin button in the corner of its tooltip. Pinned
blocks are listed newest first, and each can be folded on its own. Choose
**Unpin**, from the block's menu or with the button on the copy, to remove
it. Pins last until the page is reloaded.


Reading
-------

The settings for the text:

.. list-table::
   :header-rows: 1

   * - Setting
     - Choices
   * - Typeface
     - Sans, Serif, Legible
   * - Size
     - Small, Default, Large, Larger
   * - Line height
     - Tight, Normal, Loose
   * - Width
     - Narrow, Normal, Wide (not on phones)
   * - Theme
     - System, Light, Dark
   * - Map
     - Show or hide the map of the document. See :ref:`reading-minimap`.

The settings apply to every RSM page from the same website, and the browser
remembers them. **System** follows the light or dark mode of the computer,
and pages built without the sidebar always do.


Copy a link to this view
------------------------

The last icon (**Copy link** on a phone) copies a link to the page as you
have arranged it: the blocks you folded or opened, the symbols you renamed,
the order of reordered proofs, the pinned blocks, and the place you are
reading. Someone who opens the link sees the page the same way, with a
**Shared view** label that has a **Reset to original** button. Opening such
a link does not change the settings that the browser remembers.
