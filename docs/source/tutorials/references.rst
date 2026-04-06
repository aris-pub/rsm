.. _references-tutorial:

References and Citations
========================

Label any tag, reference it from anywhere, and readers see a tooltip
preview on hover.


Labeling and referencing
************************

Use ``:label:`` to name a tag, and ``:ref:`` to link to it:

.. rsm::

   :theorem: {
     :label: thm-main
   }
   Every labeled tag can be referenced.
   ::

   As shown in :ref:thm-main::, the result
   follows immediately.

Hover over the link to see the tooltip.


Custom display text
*******************

By default, references display as "Theorem 1" or "Remark 2". You can override
this at the reference site:

.. rsm::

   :lemma: {
     :label: lem-key
   }
   A useful lemma.
   ::

   By :ref:lem-key, our key lemma::, the
   proof is complete.


Citing sources
**************

Citations in RSM have two parts: a ``:references:`` block that defines the
bibliography, and ``:cite:`` tags that reference entries from it.

The ``:references:`` block holds bibliography entries in a subset of BibTeX
notation. Supported entry types include ``@article``, ``@book``,
``@inproceedings``, and others:

.. rsm::

   :references:

   @article{smith,
     title={Prior Work},
     author={Smith, Alice},
     journal={J. Example},
     year={2023},
   }

   @book{knuth,
     title={The Art of Computer Programming},
     author={Knuth, Donald E},
     year={2014},
     publisher={Addison-Wesley},
   }

   ::

Use ``:cite:<key>::`` anywhere in the manuscript to cite an entry. Citations
render as numbered links with tooltip previews, just like ``:ref:``:

.. rsm::

   ## Results

   Building on :cite:smith:: and the
   foundational work of :cite:knuth::,
   we extend the theory.

   :references:

   @article{smith,
     title={Prior Work},
     author={Smith, Alice},
     journal={J. Example},
     year={2023},
   }

   @book{knuth,
     title={The Art of Computer Programming},
     author={Knuth, Donald E},
     year={2014},
     publisher={Addison-Wesley},
   }

   ::

Each bibliography entry in the rendered output automatically includes backlinks
to every place in the manuscript where it was cited.

If a ``doi`` field is present, RSM renders it as a clickable external link next
to the entry:

.. rsm::

   Prior results :cite:euler:: are
   well known.

   :references:

   @article{euler,
     title={On the sums of series of
     reciprocals},
     author={Euler, Leonhard},
     journal={Commentarii academiae
     scientiarum Petropolitanae},
     year={1740},
     doi={10.48550/arXiv.math/0506415},
   }

   ::


What's next?
************

- :ref:`tooltips`: more on ``:reftext:``, display text, and equation references
- :ref:`citations-guide`: multiple citations, entry types, DOI links
