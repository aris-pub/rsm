.. _styling:

Styling with CSS
=================

RSM manuscripts are rendered as HTML, which means you can apply CSS classes to any tag
using the ``:class:`` meta tag. This allows you to customize the appearance of your
manuscript without writing custom HTML.

How :class: works
*****************

The ``:class:`` meta tag accepts one or more CSS class names (separated by spaces) and
applies them to the rendered HTML element. RSM includes built-in CSS classes for common
styling needs, and you can also use custom CSS classes if you provide your own stylesheet.

Basic syntax
------------

.. code-block:: text

   :tag: {:class: class-name} content ::

Or for block tags:

.. code-block:: text

   :tag: {
     :class: class-name another-class
   }

   Content here.

   ::

Built-in CSS classes
********************

RSM provides several built-in CSS classes you can use immediately.

Font sizes
----------

RSM includes pre-defined font size classes:

.. rsm::

   :paragraph: {:class: tiny} Tiny text (0.6rem)

   :paragraph: {:class: smallest} Smallest text (0.7rem)

   :paragraph: {:class: smaller} Smaller text (0.8rem)

   :paragraph: {:class: small} Small text (0.9rem)

   :paragraph: {:class: normal} Normal text (1rem)

   :paragraph: {:class: large} Large text (1.2rem)

   :paragraph: {:class: larger} Larger text (1.4rem)

   :paragraph: {:class: largest} Largest text (1.6rem)

   :paragraph: {:class: huge} Huge text (2rem)

   :paragraph: {:class: huger} Huger text (2.5rem)

These font size classes work on any tag: blocks, inlines, paragraphs, or even math:

.. rsm::

   Normal equation: $E = mc^2$

   Large equation: $ {:class: large} E = mc^2 $

   Huge equation: $ {:class: huge} E = mc^2 $

Practical examples
******************

Emphasizing important theorems
-------------------------------

Combine ``:class:`` with multiple classes for custom styling:

.. rsm::

   :theorem: {
     :title: Main Result
     :class: large
   }

   This is our central theorem, displayed
   in a larger font.

   ::

Small notes and asides
----------------------

Use smaller font sizes for footnotes or side comments:

.. rsm::

   The main argument proceeds as follows...

   :paragraph: {:class: small} Note: This
   proof technique was first used by Euler
   in 1750.


Multiple classes
----------------

You can apply multiple CSS classes by separating them with spaces:

.. code-block:: text

   :span: {:class: type1 type2} Styled text ::

   :block-tag: {
     :class: type1 type2
   }
   Styled text
   ::


Using custom CSS
****************

By default, the ``rsm`` CLI utilities will search the current working directory for a
css file with the same name as the file you are processing. For example,

.. code-block:: bash

   $ rsm build manuscript.rsm

Will include ``manuscript.css`` if it exists. To use a file with a different name, use
the ``--css`` flag.

.. code-block:: bash

   $ rsm build manuscript.rsm --css styles.css

Then in your RSM manuscript, reference your custom classes:

.. code-block:: text

   :paragraph: {:class: my-custom-class} Styled content ::

Your CSS file should define the class:

.. code-block:: css

   .my-custom-class {
     color: #007acc;
     border-left: 4px solid #007acc;
     padding-left: 1em;
   }

Complete example
----------------

Here's a full example showing custom CSS in action:

.. rsm::
   :custom-css: _static/custom-example.css

   ## RSM Styling

   :span:{:class: highlight-box} This
   phrase:: has a custom highlight style
   with a colored border and background.

   :theorem: {
     :title: Main Theorem
     :class: emphasis-theorem
   }
   This theorem uses custom styling to
   stand out from regular theorems.
   ::

To create this, you would write the RSM source above and define these CSS classes:

.. code-block:: css

   .highlight-box {
     background-color: #fff3cd;
     border-left: 4px solid #ffc107;
   }

   .emphasis-theorem {
     background-color: #e7f3ff;
     border: 2px solid #0066cc;
     padding: 1.5em;
     border-radius: 8px;
   }

Save your RSM source as ``manuscript.rsm`` and your CSS as ``manuscript.css``. Build with:

.. code-block:: bash

   $ rsm build manuscript.rsm

The CSS file will be automatically included since it has the same name as the RSM file.

Best practices
**************

.. warning::

   **Keep styling semantic**: Use ``:class:`` for presentation only, not content structure or
   document layout.

   Don't use ``:class:`` to fake structural elements like headings, sections, or theorems.
   If you need a theorem, use ``:theorem:``. If you need a section, use ``##``. Don't
   create a paragraph with custom styling to look like a theorem, as that breaks semantic
   meaning and accessibility.

   The ``:class:`` meta tag is for *how something looks*, not *what it is*.

   **If you find yourself using** ``:class:`` **to override RSM's default behavior for semantic
   tags**, please `open an issue <https://github.com/aris-pub/rsm/issues>`_ or contribute to
   the language. The defaults should work for most cases. If they don't for you, we want to know.

1. **Use built-in classes first**: RSM's built-in classes handle common cases and work
   consistently across themes.

2. **Test across themes**: If providing custom CSS, test your manuscript in both light
   and dark themes.

3. **Avoid inline styles**: RSM doesn't support inlined HTML/CSS. Always use CSS classes
   via ``:class:``.

See also
********

- :ref:`recipes` for more styling examples
- :ref:`syntax` for complete ``:class:`` meta tag syntax
