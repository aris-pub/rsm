.. _ref-figures-tables:

Figures, tables and video
=========================

Figures and videos are numbered within their section, such as Figure 2.1.
Tables are numbered through the whole document, such as Table 3. Each kind has
its own counter.

Every tag on this page also takes the meta keys that all tags take, such as
``:label:`` and ``:nonum:``. See :ref:`ref-meta-keys`.


.. _tag-figure:

``:figure:``
------------

An image, or an interactive figure written in HTML, with an optional caption.

.. rsm::
   :source-only:

   :figure: {:path: <file>, :alt: <description>}
     :caption: <caption>
   ::

Meta keys:

``:path:``
   The file to show, relative to the ``.rsm`` file. A PNG, JPEG, GIF or SVG
   file is shown as an image. An HTML file is copied into the page as it is,
   scripts included.

``:alt:``
   A sentence that describes the figure, for readers who cannot see it.

``:static:``
   An image of the figure, shown instead of HTML in tooltips, in exported
   files and on a page with JavaScript turned off. The reader can also switch
   to it with the "Static" item in the handrail menu. See
   :ref:`tutorial-figures`.

``:dark:``
   A second image, shown instead of ``:path:`` when the reader's system is in
   dark mode.

``:scale:``
   A number that multiplies the width of the image, such as ``0.5``.

``:blockname:``
   A name that replaces "Figure" in the figure's label and in references to
   it, such as ``Diagram``.

``:as-paragraph:``
   Shows the figure as part of the text, with no number and no caption. A
   caption inside the figure is dropped, with a warning.

Instead of ``:path:``, a figure can hold an ``:htmlblock:`` with its HTML
written in the document.

.. rsm::

   ## Results

   :figure: {
     :label: fig-plot,
     :path: _static/images/performance-plot.svg,
     :alt: Line chart of R² score against dataset size for three models.
   }
     :caption: R² score of three models.
   ::

   :ref:fig-plot:: has three lines.

Related: :ref:`tag-caption`, :ref:`tag-video`.


.. _tag-video:

``:video:``
-----------

A video file, with the browser's controls and an optional caption.

.. rsm::
   :source-only:

   :video: {:path: <file>}
     :caption: <caption>
   ::

Meta keys:

``:path:``
   The video file, relative to the ``.rsm`` file: MP4, WebM or MOV.

``:blockname:``, ``:as-paragraph:``
   As for ``:figure:``.

Related: :ref:`tag-figure`, :ref:`tag-caption`.


.. _tag-table:

``:table:``
-----------

A table, with an optional head, a body and an optional caption, in that order.

.. rsm::
   :source-only:

   :table:
     :thead:
       :tr: <cell> : <cell> ::
     ::
     :tbody:
       :tr: <cell> : <cell> ::
     ::
     :caption: <caption>
   ::

Meta keys:

``:blockname:``
   A name that replaces "Table" in the table's label and in references to it.

.. rsm::

   :table: {:label: tbl-sizes}
     :thead:
       :tr: Dataset : Rows ::
     ::
     :tbody:
       :tr: Small : $10^3$ ::
       :tr: Large : $10^6$ ::
     ::
     :caption: Sizes of the two datasets.
   ::

   :ref:tbl-sizes:: lists the datasets.

Related: :ref:`tag-tr`, :ref:`tag-caption`.


.. _tag-thead:
.. _tag-tbody:

``:thead:`` and ``:tbody:``
---------------------------

The head and the body of a ``:table:``. Each holds one or more rows and ends
with ``::``. The rows of the head have a gray background.

Related: :ref:`tag-table`, :ref:`tag-tr`.


.. _tag-tr:
.. _tag-td:

``:tr:`` and ``:td:``
---------------------

A row of a table, and a cell of a row. A row starts with ``:tr:`` and ends
with ``::``. Its cells can be written in two ways:

- Separated by ``:``, as in ``:tr: Small : $10^3$ ::``.
- Each in its own ``:td:``, as in ``:tr: :td: Small :: :td: $10^3$ :: ::``.

A cell can hold text and inline markup, such as math, emphasis and
references.

Related: :ref:`tag-table`.


.. _tag-caption:

``:caption:``
-------------

The caption of a ``:figure:``, ``:video:`` or ``:table:``. It goes inside the
block, after its content, and runs to the block's closing ``::``. RSM puts
the block's label, such as "Figure 1.1.", before it.

Related: :ref:`tag-figure`, :ref:`tag-video`, :ref:`tag-table`.
