.. _bibliography:

Bibliography
============

RSM supports bibliography using BibTex notation. Use the ``:references:`` tag to note
where in the manuscript the list of references will appear.

.. rsm::

   ## Some section

   Some content here :cite:knuth::.

   :references:

   @book{knuth,
         title={Art of computer programming,
         volume 2, Seminumerical algorithms},
         author={Knuth, Donald E},
         year={2014},
         publisher={Addison-Wesley
         Professional},
         doi={10.1137/1012065},
        }

   ::

Within the manuscript contents, use ``:cite:`` to refer to a bibliography item.

Much like references, citations always display with a tooltip.  Similarly, each
bibliography item in the generated reference list contains backlinks, also with
tooltips, to those places in the manuscript where the item has been cited.  Finally, RSM
will automatically add a link to the DOI of the referenced work, if available.
