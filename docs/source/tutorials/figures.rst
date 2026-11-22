.. _tutorial-figures:

Figures and tables
==================

This lesson adds an image and a table to a document, with numbers and
captions.

.. rsm::

   # Results

   ## Data

   :figure: {
     :label: fig-plot,
     :path: _static/images/performance-plot.svg,
     :alt: Line chart of R² score against dataset size for three models.
   }

     :caption: R² score of three models for datasets of different sizes.

   ::

   The figure has a number, and :ref:fig-plot:: links to it.

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


Figures
-------

``:figure:`` holds an image. Its meta keys are:

- ``:path:``, the image file, relative to the ``.rsm`` file. PNG, JPEG and
  SVG work.
- ``:alt:``, a sentence that describes the image for readers who cannot see
  it, such as people who use a screen reader. Always write one.
- ``:label:``, so that you can refer to the figure.

Inside the figure, ``:caption:`` holds the caption, and ``::`` ends the
figure.

When you build a document, RSM copies the image files into an ``assets/``
folder next to the HTML file.

A figure can also hold an interactive widget written in HTML, or a video. See
:ref:`guide-interactive-figures` for both.


Tables
------

``:table:`` holds a table, made of a head, ``:thead:``, and a body,
``:tbody:``. Each ends with ``::``.

Each row starts with ``:tr:`` and ends with ``::``. Inside a row, ``:``
separates the cells, so ``:tr: Small : $10^3$ ::`` is a row with two cells.

A table can have a ``:label:``, as a figure can, and its ``:caption:`` goes
after the body.

The next lesson is :ref:`tutorial-build`.
