.. _tutorial-figures:

Figures and tables
==================

On this page you add an interactive figure and a table to a document, with
numbers and captions.

.. rsm::

   # Results

   ## Data

   :figure: {
     :label: fig-r2,
     :path: _static/figures/r2-plot.html,
     :static: _static/figures/r2-plot.svg,
     :alt: Line chart of R² score against dataset size for three models.
   }
     :caption: R² score of three models for datasets of different sizes.
   ::

   Hover over the lines in :ref:fig-r2:: to read each value.

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

``:figure:`` holds an image, or an interactive figure written in HTML. Its
meta keys are:

- ``:path:``, the file, relative to the ``.rsm`` file. An image can be PNG,
  JPEG or SVG. An HTML file is copied into the page as it is, scripts
  included, so a chart made with a library such as Plotly works in the page.
  The figure above is a Plotly chart.
- ``:static:``, an image of the same figure, for the places where the HTML
  cannot run.
- ``:alt:``, a sentence that describes the figure for readers who cannot see
  it, such as people who use a screen reader. Always write one.
- ``:label:``, so that you can refer to the figure.

Inside the figure, ``:caption:`` holds the caption, and ``::`` ends the
figure.

When you build a document, RSM copies the image files into an ``assets/``
folder next to the HTML file.


The static version of a figure
------------------------------

RSM shows the image in ``:static:`` instead of the HTML in these places:

- the tooltip of a reference to the figure, such as the one on
  :ref:fig-r2:: above,
- a page opened with JavaScript turned off,
- the PDF, LaTeX and other files that RSM makes from a document.

A reader can also switch a figure to its static version, and back, with the
"Static" item in the figure's handrail menu. Try it on the figure above.

Without ``:static:``, the tooltip of an HTML figure shows its ``:alt:`` text,
a page with JavaScript turned off shows nothing in its place, and the files
that RSM makes show a note that points to the web page. To make the static image of a Plotly chart, use the camera button
above the chart, or ``Plotly.toImage`` in a script.

See :ref:`guide-interactive-figures` for HTML written inside the document and
for videos.


Tables
------

``:table:`` holds a table, made of a head, ``:thead:``, and a body,
``:tbody:``. Each ends with ``::``.

Each row starts with ``:tr:`` and ends with ``::``. Inside a row, ``:``
separates the cells, so ``:tr: Small : $10^3$ ::`` is a row with two cells.

A table can have a ``:label:``, as a figure can, and its ``:caption:`` goes
after the body.
