.. _recipes:

Recipes
=======

Change font size
****************

There exist pre-determined types that can be added to any tag to change font size.

.. rsm::

   :paragraph: {:types: tiny} Lorem ipsum.

   :paragraph: {:types: smallest} Lorem ipsum.

   :paragraph: {:types: smaller} Lorem ipsum.

   :paragraph: {:types: small} Lorem ipsum.

   :paragraph: {:types: normal} Lorem ipsum.

   :paragraph: {:types: large} Lorem ipsum.

   :paragraph: {:types: larger} Lorem ipsum.

   :paragraph: {:types: largest} Lorem ipsum.

   :paragraph: {:types: huge} Lorem ipsum.

   :paragraph: {:types: huger} Lorem ipsum.

These work on blocks, inlines, paragraphs, or even math blocks.

.. rsm::

   $ {:types: tiny} 2 + 2 = 4$

   $ {:types: smallest} 2 + 2 = 4$

   $ {:types: smaller} 2 + 2 = 4$

   $ {:types: small} 2 + 2 = 4$

   $ {:types: normal} 2 + 2 = 4$

   $ {:types: large} 2 + 2 = 4$

   $ {:types: larger} 2 + 2 = 4$

   $ {:types: largest} 2 + 2 = 4$

   $ {:types: huge} 2 + 2 = 4$

   $ {:types: huger} 2 + 2 = 4$


Prevent automatic numbering
***************************

By default, all sections (and subsections) are numbered.  Prevent numbering of a section
by using ``:nonum:``.

.. rsm::

   ## First

   ## Unnumbered
   {:nonum:}

   ## Second

Other numbered blocks such as math blocks also accept ``:nonum:``.

.. rsm::

   $$
   2 + 2 = 4
   $$

   $$ {:nonum:}
   3 + 3 = 6
   $$

   $$
   4 + 4 = 8
   $$


Add figures
***********

Include images in your manuscript:

.. rsm::

   :figure: {
     :label: fig-example
     :caption: A simple diagram showing the concept.
     :path: images/diagram.png
   } ::

Reference the figure with ``:ref:fig-example::``.


Add inline math
***************

Use dollar signs for inline equations:

.. rsm::

   The quadratic formula is $x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$.


Add display math
****************

Use double dollar signs for display equations:

.. rsm::

   $$
   E = mc^2
   $$


Add cross-references
********************

Label any block and reference it later:

.. rsm::

   ## Introduction {
     :label: intro
   }

   Some content here.

   ## Methods

   As discussed in :ref:intro::, we proceed by...


Add code blocks
***************

Include syntax-highlighted code:

.. rsm::

   :codeblock: {:lang: python}

   def fibonacci(n):
       if n <= 1:
           return n
       return fibonacci(n-1) + fibonacci(n-2)

   ::


Add theorems and proofs
***********************

Structure mathematical arguments:

.. rsm::

   :theorem: {
     :label: thm-main
     :title: Fundamental Result
   }

   Every even integer greater than 2 can be expressed as the sum of two primes.

   ::

   :proof:

   The proof is left as an exercise.

   ::
