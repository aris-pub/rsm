.. _citations-guide:

Adding Citations and Bibliography
=================================

This guide covers adding a bibliography and citing sources in your RSM
manuscript.


Adding a references section
----------------------------

Use the ``:references:`` tag to define your bibliography. Entries use BibTeX
notation:

.. rsm::

   ## Results

   Our results extend the work of
   :cite:knuth::.

   :references:

   @book{knuth,
         title={The Art of Computer
         Programming},
         author={Knuth, Donald E},
         year={2014},
         publisher={Addison-Wesley
         Professional},
         doi={10.1137/1012065},
        }

   ::


Citing sources
--------------

Use ``:cite:<key>::`` to cite a bibliography entry anywhere in your manuscript.
The citation renders as a numbered link with a tooltip preview.


Multiple citations
------------------

Cite multiple sources by using separate ``:cite:`` tags:

.. rsm::

   ## Discussion

   Building on :cite:author1:: and
   :cite:author2::, we show that...

   :references:

   @article{author1,
     title={First Paper},
     author={Smith, Alice},
     journal={J. Example},
     year={2023},
   }

   @article{author2,
     title={Second Paper},
     author={Jones, Bob},
     journal={J. Example},
     year={2024},
   }

   ::


Supported entry types
---------------------

RSM supports these BibTeX entry types: ``@book``, ``@article``, ``@inproceedings``,
``@software``, ``@phdthesis``, ``@mastersthesis``, ``@techreport``, ``@misc``.

Each entry can include: ``title``, ``author``, ``year``, ``journal``, ``publisher``,
``doi``, ``url``, ``volume``, ``number``, ``pages``, ``booktitle``, ``note``,
``editor``, ``institution``, ``school``, ``howpublished``.

When a ``doi`` is provided, RSM automatically adds a clickable DOI link to the
rendered bibliography entry.

.. tip::

   Each bibliography item in the rendered output includes backlinks to every
   place in the manuscript where it was cited.
