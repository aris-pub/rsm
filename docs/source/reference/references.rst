.. _ref-references:

References, links and citations
===============================

A reference links to a part of the same document that has a ``:label:``. A
link goes to a web page. A citation points to an entry in the list of
references. In the built page, the reader can hover over a reference or a
citation, or tap it on a phone, to see what it points to in a tooltip.


.. _tag-ref:

.. rst-class:: tag-card

Reference ``:ref:``
-------------------

A link to the part of the document with the given label. The link text is the
kind and number of that part, such as "Theorem 2.1", "Section 3" or "(2.4)"
for an equation. Text after a comma replaces it, and can hold inline markup.

.. rubric:: Syntax

.. rsm::
   :source-only:

   ## Section {:label: <label>}

   See :ref:<label>:: and :ref:<label>, <link text>::.

.. rubric:: Example

.. rsm::

   ## Method {:label: sec-method}

   :ref:sec-method:: explains the method, and
   :ref:sec-method, the method section:: does too.

.. rubric:: Related

:ref:`Step references <tag-prev>`, :ref:`ref-meta-keys`.


.. _tag-url:

.. rst-class:: tag-card

Link ``:url:``
--------------

A link to a web page. Without a comma and link text, the address is the link
text.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :url:https://example.org, <link text>::

.. rubric:: Example

.. rsm::

   The code is at :url:https://example.org/sort, our repository::, and the
   data at :url:https://example.org/data::.

.. rubric:: Related

:ref:`Reference <tag-ref>`.


.. _tag-cite:

.. rst-class:: tag-card

Citation ``:cite:``
-------------------

A citation of one or more entries of the ``:references:`` block, by their
keys, separated by commas. By default a citation is a number in brackets,
such as [1]. The ``:citation-style:`` setting switches the whole document to
author and year. Each entry in the list of references links back to the places
where it is cited.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :cite:<key>::, :cite:<key>,<key>::

.. rubric:: Related

:ref:`Bibliography <tag-references>`, :ref:`ref-config`,
:ref:`guide-citations`.


.. _tag-references:

.. rst-class:: tag-card

Bibliography ``:references:``
-----------------------------

The list of works that the document cites, as BibTeX entries, such as a
reference manager exports. RSM prints it as a list of references, numbered or
sorted by author, and warns about an entry without a DOI. Put it at the end of
the document.

RSM reads entry kinds in capitals too, such as ``@Article``, and reads a kind
that RSM does not know, such as ``@manual``, as ``@misc``. RSM skips a field
that it does not use, such as ``keywords``, a value in quotes or a value that
is a bare word, and ``@string`` definitions. RSM ignores braces inside a value
and keeps the text inside them, and does not read LaTeX commands. Each of
these gives a warning that names the entry key and the field, and the rest of
the entry is kept. See :ref:`guide-citations` for the kinds and fields that
RSM uses.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :references:
   @book{<key>,
     title = {<title>},
     author = {<last name>, <first name>},
     year = {<year>},
     publisher = {<publisher>}
   }
   ::

.. rubric:: Entry kinds

``@article``
   Prints the journal, volume and issue.

``@book``
   Prints the publisher.

``@inproceedings``, ``@conference``
   Prints the book title of the proceedings.

``@incollection``
   Prints the book title and the publisher.

``@phdthesis``, ``@mastersthesis``
   Prints the kind of thesis and the school.

``@techreport``
   Prints the institution.

.. rubric:: Example

.. rsm::

   Sorting is covered in :cite:knuth::.

   :references:
   @book{knuth,
     title = {The Art of Computer Programming},
     author = {Knuth, Donald E.},
     year = {1998},
     publisher = {Addison-Wesley}
   }
   ::

.. rubric:: Related

:ref:`Citation <tag-cite>`.
