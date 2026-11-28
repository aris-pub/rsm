.. _guide-interactive-figures:

Interactive figures and raw HTML
================================

An RSM page is a web page, so a figure can be a chart that the reader can
hover over, zoom or drag, and the text can hold any HTML. This page shows how
to add a chart made with a plotting library, how to write HTML in the
document, and how to add a video.


Add a chart made with a plotting library
----------------------------------------

Save the chart as an HTML file next to the ``.rsm`` file, and give its path
to ``:figure:``. RSM copies the HTML into the page as it is, scripts
included:

.. rsm::

   :figure: {
     :label: fig-r2,
     :path: _static/figures/r2-plot.html,
     :static: _static/figures/r2-plot.svg,
     :alt: Line chart of R² score against dataset size for three models.
   }
     :caption: R² score of three models for datasets of different sizes.
   ::

The file must hold only the chart, not a whole web page. A file that starts
with ``<!DOCTYPE>`` or ``<html>`` stops the build with an error. With Plotly
in Python, save the chart like this:

.. code-block:: python

   fig.write_html("r2-plot.html", full_html=False, include_plotlyjs="cdn")

``full_html=False`` leaves out the page around the chart, and
``include_plotlyjs="cdn"`` loads the Plotly library from the web instead of
copying all of it into the file.

``:static:`` is an image of the same chart. RSM shows it where the HTML
cannot run, as described under "Where the reader sees the HTML" below. See
:ref:`tutorial-figures`.


Write the HTML in the document
------------------------------

For a small piece of HTML, write it in the document with ``:htmlblock:``
instead of keeping it in a file. Put the ``:htmlblock:`` inside a
``:figure:`` to give it a number and a caption:

.. rsm::

   :figure: {
     :label: fig-square,
     :alt: A slider that sets n, with the value of n squared next to it.
   }

   :htmlblock:
   <label>n = <input type="range" min="1" max="10" value="3" id="sq-n">
   <output id="sq-out">9</output></label>
   <script>
     const n = document.getElementById("sq-n");
     const out = document.getElementById("sq-out");
     n.addEventListener("input", () => {
       out.textContent = n.value * n.value;
     });
   </script>
   ::

     :caption: Drag the slider to change $n$.
   ::

   :ref:fig-square:: shows $n^2$.

``:htmlblock:`` ends at a ``::`` on a line of its own, so a ``::`` inside a
line of HTML, as in the CSS selector ``p::before``, is part of the HTML.

The HTML shares the page with the rest of the document, so an ``id`` in it,
such as ``sq-n`` above, must not be used anywhere else on the page.


Put HTML in a line of text
--------------------------

``:html:`` puts HTML inside a line of text. It ends at the first ``::``:

.. rsm::

   Water boils at :html: {:alt: 100 degrees Celsius} <b>100&nbsp;°C</b> ::
   at sea level.


Where the reader sees the HTML
------------------------------

The HTML runs on the page itself. In two places, RSM shows something else
instead:

- In the tooltip of a reference to a figure, RSM shows the ``:static:`` image
  of the figure if it has one, and its ``:alt:`` text otherwise. A second
  copy of a live chart or widget would not work in a tooltip.
- In a file exported to PDF, LaTeX or another format, a figure shows its
  ``:static:`` image. An ``:html:`` or ``:htmlblock:`` outside a figure is
  replaced by its ``:alt:`` text.

So write an ``:alt:`` for every figure and every ``:html:`` or
``:htmlblock:`` that is not inside a figure, and a ``:static:`` image for
every figure that holds HTML. ``rsm export`` stops with an error if a figure
that holds HTML has no ``:static:``, or if an ``:html:`` or ``:htmlblock:``
outside a figure has no ``:alt:``. The error gives the line of each one.


Add a video
-----------

``:video:`` shows a video file with the browser's controls. The file can be
MP4, WebM or MOV:

.. rsm::
   :source-only:

   :video: {:label: vid-demo, :path: demo.mp4, :static: demo-frame.png}
     :caption: The proof of the main lemma, step by step.
   ::

A video is numbered and referenced like a figure, as "Video 1".

A file exported to PDF, LaTeX or another format shows the ``:static:`` image
of a video, such as one frame of it, with the caption. ``rsm export`` stops
with an error if a video has no ``:static:``.

See :ref:`tag-figure`, :ref:`tag-video` and :ref:`tag-htmlblock` in the
language reference.
