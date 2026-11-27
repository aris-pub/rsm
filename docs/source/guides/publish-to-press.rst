.. _publish-to-press:

Publishing to Scroll Press
==========================

`Scroll Press <https://scroll.press>`_ is a preprint server for papers
written as web pages. Posting a paper there gives it a permanent address and
a DOI, and anyone can read it for free. This page shows how to put an RSM
paper on Press.


Build the paper for Press
-------------------------

Press takes one HTML file, or a ZIP file that holds a page with its other
files. Either build works.

A standalone build makes one HTML file with the styles, scripts and fonts
inside it:

.. code-block:: bash

   rsm build paper.rsm --standalone

This writes ``paper.html``. Upload that file.

A folder build makes ``paper.html`` and a ``static`` folder next to it, plus
an ``assets`` folder when the paper has images. To upload it, put the
folder in a ZIP file. Press opens ``index.html``, ``paper.html``,
``article.html``, ``main.html`` or ``manuscript.html`` as the page, and asks
you to pick the page when it finds none of them.

Before you upload, open the page in a browser and read it through, or run
``rsm serve paper.rsm`` and read it there.


Create an account
-----------------

Sign up at `scroll.press <https://scroll.press>`_, with an email address or
with ORCID. With an email address, Press sends a link to verify it, and you
can upload only after you click the link. An ORCID account needs no
verification.


Upload the paper
----------------

Click **New Scroll** in the top bar. The upload page asks for:

- the title, the authors (separated by commas) and the abstract, which are
  required, the subject, and the keywords, which you can leave out,
- the license: **Open Access (CC BY 4.0)** or **All Rights Reserved**,
- a box to tick, to confirm that you have the right to make the paper public,
- the file: the HTML file or the ZIP file.

Press does not read the title, the authors or the abstract from the file, so
type them as they are in the paper. You must be one of the authors: when
Press does not find the name of your account in the list, it asks which
author you are.

Click **Preview Scroll**. Press checks the file and shows the paper as it
will look when posted. Read it again there. **Edit Details** goes back to
the form, and **Discard** drops the upload.


Post the paper
--------------

Click **Post scroll**. Posting makes the paper public and cannot be undone.
Press then gives the paper:

- a permanent address, ``/scroll/`` followed by a code, and a shorter one made
  of the year and a short form of the title, such as ``/2026/graphs-without-triangles``,
- a DOI. Press asks Zenodo for it after posting, and shows it on the page
  when Zenodo has made it.

To change a posted paper, click **New Version** on its page. The form opens
with the details of the paper filled in. Upload the new file, or leave the
file out to change only the details. The new version keeps the same address,
and each version also keeps its own, such as
``/2026/graphs-without-triangles/v1``.
