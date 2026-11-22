.. _tutorial-build:

Build, preview and share a document
===================================

In this lesson you turn a ``.rsm`` file into a web page in three ways, and
put the page where readers can open it.


A folder of files
-----------------

.. code-block:: bash

   rsm build paper.rsm

This writes three things next to ``paper.rsm``:

- ``paper.html``, the page itself
- ``static/``, the fonts, styles and scripts of every RSM page
- ``assets/``, the images and other files that the document uses, if any

The page needs both folders, so keep the three together when you move or
upload them. ``-o`` sets another name or folder for the output, for example
``rsm build paper.rsm -o public/index``.


A single file
-------------

.. code-block:: bash

   rsm build paper.rsm --standalone

This writes one HTML file, with the styles, scripts and images inside it. It
is larger than the folder build, but you can send it as an email attachment or
upload it anywhere as one file.


The reader sidebar
------------------

.. code-block:: bash

   rsm build paper.rsm --sidebar

``--sidebar`` adds a sidebar to the page, with the table of contents, the
document's notation, the steps of its proofs and the parts that the reader
has pinned. See :ref:`reading` for what readers can do with it. You can give
``rsm serve`` the same option.


Preview while you write
-----------------------

.. code-block:: bash

   rsm serve paper.rsm

``rsm serve`` builds the page, opens it in your browser and rebuilds it each
time you save the source. The page is served at ``http://localhost:5500``.
``--port`` picks another port, and ``--no-browser`` skips opening the browser.


Share the page
--------------

An RSM page is plain HTML, CSS and JavaScript, and it needs no server
program. Any service that hosts static files can publish it, for example
GitHub Pages, Netlify or a university web space: upload ``paper.html`` with
its ``static/`` and ``assets/`` folders, or the single file from
``--standalone``.

`RSM Studio <https://rsm.studio>`_ is an online editor for RSM. It builds the
page as you type, lets coauthors edit together, and gives each document a
link to share.


What to read next
-----------------

You now know enough RSM to write a complete paper. From here:

- :ref:`guides`: one task per page, such as structured proofs, notation,
  footnotes and converting from LaTeX.
- :ref:`language-reference`: every tag and meta key, each with an example.
- :ref:`reading`: what a reader can do on an RSM page.
