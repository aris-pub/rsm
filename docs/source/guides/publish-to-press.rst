.. _publish-to-press:

Publishing to Scroll Press
===========================

`Scroll Press <https://scroll.press>`_ is a web-native preprint archive for HTML manuscripts. Press accepts any manuscript that renders to HTML—RSM, Quarto, Jupyter notebooks (via nbconvert), Pandoc, and more. This tutorial shows you how to publish your RSM work to Press and get a permanent URL and DOI.

What is Scroll Press?
*********************

Scroll Press is a preprint server, like arXiv, but designed for modern **web-first research**:

- **HTML-native**: No PDFs—readers get responsive, interactive manuscripts
- **Permanent URLs and DOIs**: Every paper gets a stable, citable link
- **Open access**: Free to publish, free to read
- **No gatekeeping**: Publish immediately (moderation is post-publication)

Prerequisites
*************

This tutorial focuses on publishing **RSM manuscripts** to Press. If you're using Quarto, Jupyter notebooks, or other HTML-generating tools, the workflow is similar—just skip to Step 4 (Create Account) with your HTML file ready.

Before publishing an RSM manuscript to Press, you need:

1. An RSM manuscript (a ``.rsm`` file)
2. RSM installed locally (``pip install rsm-lang``)
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

**Required fields**: Title, at least one author with name, abstract. **Recommended fields**: Author affiliation and email, abstract keywords, date.

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

   $ rsm serve

Open ``http://127.0.0.1:5500`` in your browser. Verify:

- Title and author appear correctly
- Abstract is properly formatted
- All sections, figures, and equations render
- Cross-references and citations work

Step 3: Create a Scroll Press Account
**************************************

Visit `scroll.press <https://scroll.press>`_ and sign up. After signing up, verify your
email and log in. You cannot upload a file before verifying your email.

Step 4: Upload Your Manuscript
*******************************

On your Press dashboard:

1. Click **"Publish New Scroll"**
2. Upload your standalone HTML file (``manuscript.html``)
3. Press auto-extracts metadata from your HTML manuscript
4. Review the preview
5. Click **"Publish"**

Your paper is now live!

Troubleshooting
***************

**"Upload failed: Missing required metadata"**

- Make sure your manuscript has title, author (with name), and abstract
- For RSM: Run ``rsm check manuscript.rsm`` to validate
- For other formats: Check your HTML has proper metadata tags

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
     - Web-first research
     - Broad academic
     - Broad academic
     - None

**When to use Press**:

- You value web-first reading experience
- Your paper has interactive visualizations or code
- You want responsive design (mobile-friendly)
- You're publishing in HTML format (RSM, Quarto, Jupyter, etc.)

**When to use arXiv**:

- You need immediate DOI
- Your field requires arXiv submission
- You prefer LaTeX + PDF workflow

**Why not both?**

You can publish on both Press (HTML version) and arXiv (PDF version). Many authors do this to reach both audiences.
