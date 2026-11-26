.. _styling:

Styling
=======

RSM pages come with their own stylesheet. To change how one part of a
document looks, give that part a CSS class with the ``:class:`` meta key. The
class can be one of the classes that RSM provides, or one that you define in
your own stylesheet.


Give a block or a phrase a class
--------------------------------

Write ``:class:`` in the meta keys of any tag, with one or more class names
separated by commas. It works on blocks, on paragraphs, on a phrase marked
with ``:span:``, and on math:

.. rsm::

   :paragraph: {:class: large} This paragraph is larger than the others.

   :theorem: {:class: small}
   This theorem is in a smaller font.
   ::

   Only :span: {:class: large} these words :: are larger, and so is this
   formula: $ {:class: large} E = mc^2 $.

The class goes on the HTML element for that part, as in
``<div class="paragraph large">``, so any CSS rule written for the class
applies to it.


Change the text size
--------------------

RSM provides ten size classes, from smallest to largest. The sizes are
relative to the root font size of the page.

.. list-table::
   :header-rows: 1

   * - Class
     - Size
   * - ``tiny``
     - 0.5rem
   * - ``smallest``
     - 0.7rem
   * - ``smaller``
     - 0.8rem
   * - ``small``
     - 0.9rem
   * - ``normal``
     - 1rem
   * - ``large``
     - 1.2rem
   * - ``larger``
     - 1.44rem
   * - ``largest``
     - 1.7281rem
   * - ``huge``
     - 2.0741rem
   * - ``huger``
     - 2.488rem

.. rsm::

   :paragraph: {:class: smaller} Smaller text.

   :paragraph: {:class: larger} Larger text.

   $$ {:class: larger}
   e^{i\pi} + 1 = 0
   $$


Mark text as a draft
--------------------

The ``draft`` class shows text in the accent color of the page, so that
unfinished passages stand out while you write:

.. rsm::

   The bound holds for every $n$. :span: {:class: draft} Check the case
   $n = 2$ again. ::


Write your own stylesheet
-------------------------

To define your own classes, write them in a CSS file next to the RSM file,
with the same name. For ``paper.rsm``, the stylesheet is ``paper.css``.
``rsm build`` and ``rsm serve`` add it to the page:

.. code-block:: css

   .note-box {
     border-left: 3px solid var(--primary-600);
     background: var(--surface-hover);
     padding: 0.5em 1em;
   }

To use a file with another name, pass it with ``--css``:

.. code-block:: bash

   rsm build paper.rsm --css styles.css

A folder build copies the stylesheet into the ``assets`` folder and links it
from the page. A standalone build (``--standalone``) puts the stylesheet
inside the HTML file.

The example below uses that stylesheet:

.. rsm::
   :custom-css: _static/custom-example.css

   :paragraph: {:class: note-box} This paragraph has a colored border on the
   left and a light background.


Follow the light and dark themes
--------------------------------

Readers can switch the page between a light and a dark theme. A color
written as a fixed value, such as ``#fff3cd``, stays the same in both themes,
and can be hard to read in one of them. The stylesheet of the page defines
CSS variables that change with the theme, and a rule that uses them follows
the theme:

.. list-table::
   :header-rows: 1

   * - Variable
     - Used for
   * - ``--text-body``
     - body text
   * - ``--text-subtle``
     - quieter text, such as labels
   * - ``--surface-page``
     - the page background
   * - ``--surface-hover``
     - a light background, such as the one in the example above
   * - ``--border-primary``
     - borders and rules
   * - ``--primary-600``
     - the accent color, set with ``:accent:`` in the ``:config:`` block

The ``note-box`` class above uses ``--primary-600`` and ``--surface-hover``,
so its border follows the accent color and its background follows the theme.


Use classes for looks, not for structure
----------------------------------------

A class changes how a part looks, not what it is. To write a theorem, use
``:theorem:``, and to start a section, use ``##``. A paragraph styled to look
like a theorem is not numbered and cannot be referenced.

If you need a class to change how one of the RSM tags looks in every document,
`open an issue <https://github.com/aris-pub/rsm/issues>`_, because the
default may need to change.

See :ref:`ref-meta-keys` for the ``:class:`` meta key, and :ref:`ref-cli` for
the ``--css`` option.
