.. _tutorial-references:

Labels, references and citations
================================

RSM links every part of a document that you name. In this lesson you add
labels, references to them, links to web pages, and citations of other works.

.. rsm::

   # Sorting

   ## Introduction {:label: sec-intro}

   Sorting puts a list in order. :ref:sec-alg:: gives one method, and
   :ref:sec-alg, the next section:: explains why it works.
   Knuth covers many more :cite:knuth::, and so do
   :cite:knuth,cormen::. The code is at
   :url:https://example.org/sort, our repository::.

   ## Algorithm {:label: sec-alg}

   :theorem: {:label: thm-sorted}
   Insertion sort returns a sorted list.
   ::

   See :ref:sec-intro:: and :ref:thm-sorted::.

   :references:
   @book{knuth,
     title = {The Art of Computer Programming},
     author = {Knuth, Donald E.},
     year = {1998},
     publisher = {Addison-Wesley}
   }

   @book{cormen,
     title = {Introduction to Algorithms},
     author = {Cormen, Thomas H. and Leiserson, Charles E.},
     year = {2009},
     publisher = {MIT Press}
   }
   ::


Labels
------

A label names a part of the document. Sections, results, equations, figures,
tables and list items can all have one. A label goes in the ``:label:`` meta
key:

- after a heading: ``## Algorithm {:label: sec-alg}``
- after a tag: ``:theorem: {:label: thm-sorted}``
- after the ``$$`` that opens an equation: ``$$ {:label: eq-euclid}``

A label is a single word. Letters, digits and hyphens are fine. Use each label
only once in a document. If two parts have the same label, RSM prints a
warning and references go to the first one.


References
----------

``:ref:sec-alg::`` turns into a link with the kind and number of what the
label names, here "Section 2". RSM keeps the numbers right when you move or
add sections.

To set the link text yourself, put it after a comma:
``:ref:sec-alg, the next section::``.

In the built page, a reader can hover over a reference, or tap it on a phone,
to see the part that it points to without leaving their place.


Links to web pages
------------------

``:url:https://example.org/sort, our repository::`` makes a link with the text
"our repository". Without the comma and the text, the address itself is the
link text.


Citations
---------

Citations need two things: a ``:references:`` block that lists the works, and
``:cite:`` where you cite them.

The ``:references:`` block holds entries in BibTeX format, as written by most
reference managers, and ends with ``::``. Put it at the end of the document.
RSM prints it as a numbered list of references.

``:cite:knuth::`` cites the entry with the key ``knuth``, and
``:cite:knuth,cormen::`` cites two at once. Each entry in the list of
references links back to the places where it is cited.

Citations are numbered by default. To cite by author and year instead, as in
"Knuth (1998)", see :ref:`guide-citations`.

The next lesson is :ref:`tutorial-figures`.
