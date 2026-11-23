:html_theme.sidebar_secondary.remove:
:nosearch:

.. meta::
   :title: RSM: Readable Science Markup

RSM
===

.. raw:: html

   <div class="landing-hero">
     <div>
       <p class="name">RSM<span>.</span></p>
       <p class="kicker">Readable Science Markup</p>
       <p class="tag">A markup language for mathematical and scientific papers that are read on the web.</p>
     </div>
     <div class="side">
       <div class="btns"><a class="p" href="tutorials.html">Get started</a><a class="s" href="https://rsm.studio">Try in RSM Studio</a></div>
       <code class="install">pip install rsm-lang</code>
     </div>
   </div>

   <div class="landing-why">
     <div><h3><b>1</b>Write plain text</h3><p>Theorems, proofs, figures and citations are tags. Math is LaTeX. The file is readable without any tool.</p></div>
     <div><h3><b>2</b>Get a paper that links itself</h3><p>Sections and figures are numbered, references are links with tooltips, and proofs can go step by step.</p></div>
     <div><h3><b>3</b>Publish anywhere</h3><p>One command builds a web page that any static host can serve, or a single HTML file to send.</p></div>
   </div>

   <div class="landing-next">
     <a href="tutorials.html"><b>Tutorial</b><span>Six pages, from install to publishing.</span></a>
     <a href="guides.html"><b>Guides</b><span>One task per page.</span></a>
     <a href="reference.html"><b>Reference</b><span>Every tag and option.</span></a>
     <a href="https://rsm.studio"><b>RSM Studio</b><span>Write RSM in your browser.</span></a>
   </div>

   <div class="landing-band">
     <h2>Plain text in, an interactive paper out</h2>
     <p class="sub">“source” is the file that you write. “page” is the web page that RSM builds from it.</p>

.. rsm::
   :custom-css: _static/landing-frame.css

   # Euclid's theorem

   :author: {
     :name: Euclid of Alexandria
     :affiliation: Library of Alexandria
   } ::

   :theorem: {:label: thm-inf, :title: Infinitude of primes}
   There are infinitely many primes.
   ::

   :proof:

     :step: :assume: $p_1, \dots, p_k$ are all the primes::.
     ::

     :step: :let: $N = p_1 p_2 \cdots p_k + 1$::.
     ::

     :step: :claim: no $p_i$ divides $N$::.

       :p: Each $p_i$ divides $N - 1$. ::

     ::

     :step: So a prime factor of $N$ is missing from the list,
     which contradicts the first step. :qed:
     ::

   ::

   By :ref:thm-inf::, the list of primes never ends.

.. raw:: html

     <p class="hint">In the page, hover over “Theorem 1” (or tap it on a phone) to preview it. Each proof step has a number, and the handrail on the left of each block folds it or opens its menu.</p>
   </div>

   <script>
   // Open the preview of the reference in the example once the page is ready,
   // so a first-time visitor sees what a reference does.
   window.addEventListener("load", () => {
     const f = document.querySelector(".landing-band .rsm-example-iframe");
     if (!f) return;
     const tryOpen = (n) => {
       const w = f.contentWindow, d = f.contentDocument;
       const a = d && d.querySelector("p a.reference");
       if (w && w.$ && a && w.$(a).hasClass("tooltipstered")) { w.$(a).tooltipster("open"); return; }
       if (n > 0) setTimeout(() => tryOpen(n - 1), 300);
     };
     tryOpen(20);
   });
   </script>


.. toctree::
   :maxdepth: 2
   :hidden:

   tutorials
   guides
   reading
   reference
   api
   explanation
   contributing
