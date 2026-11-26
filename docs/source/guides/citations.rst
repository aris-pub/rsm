.. _guide-citations:

Citations
=========

RSM reads the bibliography of a document as BibTeX, the format that reference
managers such as Zotero, Mendeley and JabRef export. You paste the entries into
the document, cite them by their keys, and RSM prints the citations and the
list of references.

This page builds one short document with citations. The tags are listed in
:ref:`ref-references`.


The whole document
------------------

.. rsm::

   # Notes on sorting

   ## Introduction

   Most sorting methods are covered in :cite:knuth::, and both
   :cite:knuth,sedgewick:: prove that sorting $n$ items by comparisons takes
   at least $\log_2 n!$ comparisons.

   :references:
   @book{knuth,
     title = {The Art of Computer Programming, Volume 3},
     author = {Knuth, Donald E.},
     year = {1998},
     publisher = {Addison-Wesley},
     doi = {10.5555/280635}
   }

   @book{sedgewick,
     title = {Algorithms},
     author = {Sedgewick, Robert and Wayne, Kevin},
     year = {2011},
     publisher = {Addison-Wesley},
     doi = {10.5555/2011916}
   }
   ::

The rest of this page goes through the parts of this document.


Add the bibliography
--------------------

Put a ``:references:`` block at the end of the document, and paste the BibTeX
entries into it, one after the other. Close the block with ``::``.

The key of an entry is the word after the opening brace, such as ``knuth`` in
``@book{knuth,``. Citations use this key.

RSM reads a subset of BibTeX, not everything that BibTeX and LaTeX accept.
Entries outside this subset never stop the build. RSM keeps each entry, and
gives a warning that names the entry key and the field:

- The entry kinds are ``@article``, ``@book``, ``@conference``,
  ``@incollection``, ``@inproceedings``, ``@mastersthesis``, ``@misc``,
  ``@phdthesis``, ``@software``, ``@techreport``, ``@unpublished`` and
  ``@webpage``. RSM reads them in capitals too, such as ``@Article``. RSM
  reads any other kind, such as ``@manual``, as ``@misc`` and gives a warning.
- The fields are ``title``, ``author``, ``editor``, ``year``, ``month``,
  ``journal``, ``booktitle``, ``series``, ``volume``, ``number``, ``pages``,
  ``edition``, ``publisher``, ``organization``, ``institution``, ``school``,
  ``address``, ``howpublished``, ``note``, ``doi`` and ``url``. RSM skips any
  other field, such as ``keywords`` or ``abstract``, and gives a warning.
- Each value is written in braces. RSM skips a value in quotes, such as
  ``title = "Sorting"``, or a value that is a bare word, such as
  ``journal = jcp``, and gives a warning.
- RSM ignores braces inside a value and keeps the text inside them, so
  ``{A {B} C}`` reads "A B C", and gives a warning. RSM does not read LaTeX
  commands: ``{Erd\H{o}s}`` reads ``Erd\Hos``. Write accented letters as they
  are, such as ö.
- RSM skips ``@string`` definitions and gives a warning that names each one.
- Write a percent sign in a value as ``\%``, as in
  ``title = {Sales up 50\% in a year}``, because ``%`` starts a comment in
  RSM. A ``%`` right after a brace, as in ``{% off}``, starts a comment that
  cuts the value. RSM then skips the field and gives a warning.

RSM warns about an entry without a ``doi``, because the reader cannot follow
it to the work.


Cite a work
-----------

Write ``:cite:`` and the key, and close it with ``::``, as in
``:cite:knuth::``. To cite several works at once, separate their keys with
commas, with no spaces: ``:cite:knuth,sedgewick::``.

The build gives a warning for a citation of a key that is not in the
bibliography.


Choose how citations look
-------------------------

By default a citation is a number in brackets, such as [1], and the list of
references is numbered in the order of the entries. To show the author
and year instead, set ``:citation-style:`` in the ``:config:`` block, after
the title:

.. rsm::

   # Notes on sorting

   :config: {:citation-style: author-parens-year}
   ::

   ## Introduction

   Most sorting methods are covered in :cite:knuth::.

   :references:
   @book{knuth,
     title = {The Art of Computer Programming, Volume 3},
     author = {Knuth, Donald E.},
     year = {1998},
     publisher = {Addison-Wesley},
     doi = {10.5555/280635}
   }
   ::

``author-parens-year`` prints Knuth (1998), and ``parens-author-year`` prints
(Knuth, 1998). With either one, the list of references has no numbers and is
sorted by author and then by year. The style applies to every citation in the
document. See :ref:`ref-config`.


What the reader can do
----------------------

In the built page:

- Hovering over a citation, or tapping it on a phone, shows the entry in a
  tooltip, so the reader does not have to scroll to the end of the page.
- Pointing at an entry in the list of references shows a "DOI" link to the
  work, and a "cited" line with one link back to each place that cites it. On
  a touch screen these links are always shown.
