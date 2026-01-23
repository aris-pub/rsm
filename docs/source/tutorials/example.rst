.. _example:

Example Manuscripts
===================

This page showcases complete RSM manuscripts demonstrating different use cases.

Quick Example: Blog Post Style
*******************************

A minimal manuscript for informal scientific writing.

.. rsm::

   # Why Web-First Scientific Publishing Matters

   :author: {
     :name: Jane Researcher
     :affiliation: University of the Web
     :email: jane@example.edu
   } ::

   :abstract:
   Traditional PDF-based scientific publishing doesn't adapt to modern reading habits.
   This post explores why web-native formats are the future of research communication.
   ::

   ## The Problem with PDFs

   Academic papers are still published primarily as PDFs, a format designed in the 1990s
   for *printing*, not *reading on screens*. This creates several issues:

   - PDFs have **fixed layouts** that don't adapt to mobile devices
   - **Interactive content** (data visualizations, embedded code) is impossible
   - **Accessibility** features (screen readers, high contrast) are limited

   ## Why HTML?

   HTML is the native format of the web. Modern HTML publications can:

   - Adapt to any screen size (responsive design)
   - Include interactive visualizations using :code:D3.js:: or :code:Observable::
   - Support screen readers and accessibility standards
   - Enable rich cross-referencing with tooltips

   As one researcher :span:{:emphas:} recently noted::, *"Reading papers on mobile
   should be as natural as reading any other web content."*

   ## Getting Started

   Try writing your next preprint in RSM and publishing it on
   `Scroll Press <https://scroll.press>`_. Your readers will thank you.


Mathematical Paper Example
**************************

A research article with theorems, proofs, and structured mathematics.

.. rsm::

   # A Note on Graph Connectivity

   :author: {
     :name: Prof. Alice Mathematician
     :affiliation: Institute of Pure Mathematics
   } ::

   :abstract:
   We present a short proof of a classical result in graph theory, demonstrating
   RSM's structured proof capabilities.
   ::

   ## Introduction

   :let: $G = (V, E)$ be an undirected graph::. We say $G$ is **connected** if
   there exists a path between any two vertices.

   :definition: {
     :label: def-component
   }

   A **connected component** of $G$ is a maximal connected subgraph.

   ::

   ## Main Result

   :theorem: {
     :title: Component Bound
     :label: thm-main
   }

   :let: $G$ be a graph with $n$ vertices and $m$ edges::. Then :claim:{:label:goal}
   $G$ has at most $n - m$ connected components::.

   ::

   :proof:

     :step: {:label:base-case}

       For the base case, :assume: $m = 0$ (no edges)::.

       :p: Then each vertex is its own component, so there are exactly $n$
       components. The bound holds with equality. :: ::

     :step: {:label:induction-step}

       For the inductive step, :assume: the theorem holds for graphs with $m - 1$ edges::.

       :p:

         :step: :let: $e = \{u, v\}$ be any edge in $G$::, and :write: $G' := G - e$
         for the graph with $e$ removed::. ::

         :step: By the induction hypothesis, $G'$ has at most $n - (m-1) = n - m + 1$
         components. ::

         :step: Adding $e$ back either merges two components (decreasing the count by 1)
         or leaves the count unchanged. ::

         :step: Therefore, $G$ has at most $(n - m + 1) - 1 = n - m$ components. ::

       :: ::

     :step: :ref:goal, The claim:: follows by induction. :qed: ::

   ::

   ## Remarks

   The bound in :ref:thm-main:: is tight: the complete graph on $n$ vertices
   achieves equality when $m = \binom{n}{2}$.


Experimental Results Example
*****************************

A paper with code, data, and visualizations (conceptual—RSM doesn't execute code).

.. rsm::

   # Machine Learning Performance on Small Datasets

   :author: {
     :name: Dr. Bob Data
     :affiliation: Center for Applied ML
   } ::

   :abstract:
   We compare three popular ML algorithms on datasets with fewer than 1000 samples.
   Our results suggest that simpler models often outperform complex neural networks
   in low-data regimes.
   ::

   ## Methodology

   We tested three algorithms:

   1. **Linear Regression** (baseline)
   2. **Random Forest** (ensemble method)
   3. **Small Neural Network** (3 hidden layers)

   Datasets ranged from 100 to 1000 samples, with 10 features each.

   ## Implementation

   All experiments used Python with scikit-learn:

   :codeblock: {:lang: python}

   from sklearn.ensemble import RandomForestRegressor
   from sklearn.linear_model import LinearRegression
   from sklearn.neural_network import MLPRegressor

   # Train models
   models = {
       'linear': LinearRegression(),
       'rf': RandomForestRegressor(n_estimators=100),
       'nn': MLPRegressor(hidden_layers=(64, 32, 16))
   }

   for name, model in models.items():
       model.fit(X_train, y_train)
       score = model.score(X_test, y_test)
       print(f"{name}: R² = {score:.3f}")

   ::

   ## Results

   The results are shown in the figure below (note: this example uses a placeholder
   since we don't have an actual image file).

   Linear regression achieves the best performance on datasets with fewer than 500 samples.

   ## Conclusion

   In low-data regimes, **simpler is better**. Before reaching for deep learning,
   try linear models—they're interpretable, fast, and often more accurate.

   :references:

   @article{breiman2001random,
     title={Random forests},
     author={Breiman, Leo},
     journal={Machine learning},
     year={2001},
     doi={10.1023/A:1010933404324}
   }

   ::


Try These Examples
******************

All three examples are valid RSM syntax. Try them:

1. Copy any example to a file (e.g., ``example.rsm``)
2. Run: ``rsm build example.rsm``
3. Open ``index.html`` in your browser
4. Experiment: modify the content and rebuild

.. tip::

   Use ``rsm serve example.rsm`` to automatically rebuild on changes.

More examples available at:

- `RSM Studio Gallery <https://rsm.studio/gallery>`_ (when available)
- `Scroll Press <https://scroll.press>`_ (real published papers)
- `/rsm-examples/ <https://github.com/leotrs/rsm/tree/main/rsm-examples>`_ folder in GitHub repo
