.. _publish-to-press:

Publishing to Scroll Press
===========================

`Scroll Press <https://scroll.press>`_ is a web-native preprint archive for RSM manuscripts. This tutorial shows you how to publish your RSM work to Press and get a permanent URL (DOI support coming soon).

What is Scroll Press?
*********************

Scroll Press is like arXiv, but designed for **web-first research** in 2026:

- **HTML-native**: No PDFs—readers get responsive, interactive manuscripts
- **Permanent URLs**: Every paper gets a stable, citable link
- **Open access**: Free to publish, free to read
- **No gatekeeping**: Publish immediately (moderation is post-publication)

Currently in **closed beta**—sign up at `scroll.press <https://scroll.press>`_ for early access.

Prerequisites
*************

Before publishing to Press, you need:

1. An RSM manuscript (a ``.rsm`` file)
2. RSM installed locally (``pip install rsm-markup``)
3. A built HTML version of your manuscript

If you don't have a manuscript yet, see :ref:`first-manuscript` or :ref:`example` for templates.

Step 1: Prepare Your Manuscript
********************************

Make sure your manuscript has complete metadata:

.. code-block:: text

   # Your Paper Title

   :author: {
     :name: Your Name
     :affiliation: Your Institution
     :email: you@example.edu
   } ::

   :abstract:
   A brief summary of your paper (1-3 paragraphs).
   ::

   :keywords: machine learning, graphs, visualization

   ## Introduction

   Your content here...

**Required fields**:

- Title (using ``#`` or ``:title:``)
- At least one author with name
- Abstract

**Recommended fields**:

- Author affiliation and email
- Keywords (helps with discovery)
- Date (defaults to today if omitted)

Step 2: Build Your Manuscript
******************************

Generate a standalone HTML file:

.. code-block:: bash

   $ rsm build manuscript.rsm --standalone

This creates a single ``manuscript.html`` file with all assets inlined (CSS, JavaScript, fonts).

.. note::

   **Beta Limitation**: Press currently only accepts single HTML files during beta. Use the ``--standalone`` flag to inline all assets. Support for external static folders is coming after beta.

**Check the output**:

.. code-block:: bash

   $ rsm serve manuscript.rsm

Open ``http://127.0.0.1:5500`` in your browser. Verify:

- Title and author appear correctly
- Abstract is properly formatted
- All sections, figures, and equations render
- Cross-references and citations work

Step 3: Create a Scroll Press Account
**************************************

Visit `scroll.press <https://scroll.press>`_ and sign up.

.. note::

   **Beta Status**: Press is currently in closed beta. Request access at the website. You'll receive an invite email within 1-2 weeks.

After signing up, verify your email and log in.

Step 4: Upload Your Manuscript
*******************************

On your Press dashboard:

1. Click **"Publish New Paper"**
2. Upload your standalone HTML file (``manuscript.html``)
3. Press auto-extracts metadata from your RSM manuscript
4. Review the preview
5. Click **"Publish"**

Your paper is now live!

.. note::

   During beta, Press only accepts single HTML files. Make sure you built with ``--standalone`` flag.

Step 5: Share Your Paper
************************

After publishing, you get:

- **Permanent URL**: ``https://scroll.press/papers/[unique-id]``
- **Shareable link**: Copy and paste anywhere
- **Citation format**: BibTeX, APA, MLA (auto-generated)
- **DOI**: Coming soon (in beta, you get permanent URLs but not yet DOIs)

Example citation:

.. code-block:: bibtex

   @article{torres2026webfirst,
     title={Why Web-First Scientific Publishing Matters},
     author={Torres, Leo},
     year={2026},
     journal={Scroll Press},
     url={https://scroll.press/papers/abc123def456}
   }

Updating Your Paper
*******************

Press supports **versioning**. To publish an update:

1. Edit your ``manuscript.rsm`` file
2. Rebuild with standalone flag: ``rsm build manuscript.rsm --standalone``
3. Go to your paper's page on Press
4. Click **"Upload New Version"**
5. Upload the updated HTML file

Each version gets a unique URL (e.g., ``/papers/abc123def456/v2``), and the main URL always points to the latest version.

Troubleshooting
***************

**"Upload failed: Missing required metadata"**

- Make sure your manuscript has title, author (with name), and abstract
- Run ``rsm check manuscript.rsm`` to validate

**"Upload failed: File too large"**

- During beta, Press has file size limits for single HTML files
- Try removing large embedded images or simplifying content
- Report if you hit this limit - we're working on solutions

**"Math equations not rendering"**

- Make sure you built with ``--standalone`` flag (embeds MathJax)
- If math works locally but not on Press, report as a bug

**"My paper isn't showing up in search"**

- Press indexes papers every 24 hours
- Add keywords to your manuscript to improve discoverability

Comparison: Press vs. Other Archives
*************************************

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - Feature
     - Scroll Press
     - arXiv
     - OSF Preprints
     - Personal Website
   * - Format
     - HTML (web-native)
     - PDF (print-native)
     - PDF
     - HTML (manual)
   * - DOIs
     - Coming soon
     - Yes
     - Yes
     - No
   * - Interactive content
     - Yes (native)
     - No
     - No
     - Yes (manual)
   * - Responsive design
     - Yes (automatic)
     - No
     - No
     - If you code it
   * - Versioning
     - Yes
     - Yes
     - Limited
     - Manual
   * - Permanent URLs
     - Yes
     - Yes
     - Yes
     - Depends on hosting
   * - Cost
     - Free
     - Free
     - Free
     - Hosting costs
   * - Community
     - RSM-focused
     - Broad academic
     - Broad academic
     - None

**When to use Press**:

- You value web-first reading experience
- Your paper has interactive visualizations or code
- You want responsive design (mobile-friendly)
- You're publishing in RSM format

**When to use arXiv**:

- You need immediate DOI
- Your field requires arXiv submission
- You prefer LaTeX + PDF workflow

**Why not both?**

You can publish on both Press (HTML version) and arXiv (PDF version). Many authors do this to reach both audiences.

Next Steps
**********

After publishing to Press:

- Share your paper on social media (Twitter, Mastodon, LinkedIn)
- Add it to your CV and personal website
- Submit to conferences or journals (Press papers are citable)
- Engage with readers (Press supports comments—coming soon)

.. tip::

   **Dogfooding**: If you're developing tools for RSM or Press, publish your documentation and blog posts as Press papers. It's great dogfooding and helps build the community.

Resources
*********

- `Scroll Press Documentation <https://scroll.press/docs>`_
- `Press GitHub Repository <https://github.com/leotrs/press>`_ (open source)
- `RSM to Press Workflow Video <https://www.youtube.com/watch?v=...>`_ (coming soon)
- Community forum: https://rsm.studio/community (coming soon)

.. admonition:: Feedback Welcome

   Press is in beta. If you encounter bugs or have feature requests, please open an issue on `GitHub <https://github.com/leotrs/press/issues>`_.
