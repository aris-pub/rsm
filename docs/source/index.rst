:html_theme.sidebar_secondary.remove:
:nosearch:

.. meta::
   :title: RSM: Readable Science Markup

.. raw:: html

   <div class="hero-section">
     <h1>RSM<span class="hero-dot">.</span></h1>
     <p class="hero-subtitle">Readable Science Markup</p>
     <p class="hero-tagline">
       A markup language for web-first scientific manuscripts.
       The simplicity of Markdown. The power of semantic tagging.
       Interactive cross-references, structured proofs, and accessible
       typography, out of the box.
     </p>
     <div class="hero-actions">
       <a href="https://rsm.studio" class="btn-primary">Try in Studio</a>
       <a href="tutorials/getting-started.html" class="btn-secondary">Get Started →</a>
     </div>
   </div>


A taste of RSM
--------------

.. rsm::

   # Euler's Identity

   :author: {
     :name: Jane Scientist
     :affiliation: Example University
   } ::

   :abstract:
   A brief demonstration of RSM markup.
   ::

   ## Introduction

   RSM combines the simplicity of Markdown
   with the power of semantic tagging.
   Write **bold**, *italic*, and
   :math: e^{i\pi} + 1 = 0 :: inline.

   :theorem: {
     :label: thm-demo
     :title: Main Result
   }
   Every RSM tag can be labeled and
   cross-referenced with automatic tooltips.
   ::

   :proof:
   The proof follows from :ref:thm-demo::.
   ::


Explore the docs
----------------

.. grid:: 1 2 2 2

   .. grid-item-card:: Tutorials
      :link: tutorials.html

      Step-by-step lessons for learning RSM from scratch.


   .. grid-item-card:: How-to Guides
      :link: guides.html

      Task-oriented guides for styling, citations, and publishing.


   .. grid-item-card:: Reference
      :link: reference.html

      Complete reference for syntax, configuration, CLI, and API.


   .. grid-item-card:: Explanation
      :link: explanation.html

      Design decisions and comparisons with LaTeX and Markdown.


.. toctree::
   :maxdepth: 2
   :hidden:

   tutorials
   guides
   reference
   explanation
   contributing
