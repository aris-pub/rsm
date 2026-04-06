.. _recipes:

Recipes
=======

Change font size
****************

There exist pre-determined types that can be added to any tag to change font size.

.. rsm::

   :paragraph: {:class: tiny} Lorem ipsum.

   :paragraph: {:class: smallest} Lorem ipsum.

   :paragraph: {:class: smaller} Lorem ipsum.

   :paragraph: {:class: small} Lorem ipsum.

   :paragraph: {:class: normal} Lorem ipsum.

   :paragraph: {:class: large} Lorem ipsum.

   :paragraph: {:class: larger} Lorem ipsum.

   :paragraph: {:class: largest} Lorem ipsum.

   :paragraph: {:class: huge} Lorem ipsum.

   :paragraph: {:class: huger} Lorem ipsum.

These work on blocks, inlines, paragraphs, or even math blocks.

.. rsm::

   $ {:class: tiny} 2 + 2 = 4$

   $ {:class: smallest} 2 + 2 = 4$

   $ {:class: smaller} 2 + 2 = 4$

   $ {:class: small} 2 + 2 = 4$

   $ {:class: normal} 2 + 2 = 4$

   $ {:class: large} 2 + 2 = 4$

   $ {:class: larger} 2 + 2 = 4$

   $ {:class: largest} 2 + 2 = 4$

   $ {:class: huge} 2 + 2 = 4$

   $ {:class: huger} 2 + 2 = 4$


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
     :path: _static/images/diagram.svg
   }
   :caption: A simple diagram showing the concept.
   ::

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
