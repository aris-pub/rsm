.. _ref-tabs:

Tabs
====

Tabs show one of several versions of the same material at a time, such as a
sketch and a full proof. The reader picks one in a row of tabs.


.. _tag-tabs:
.. _tag-tab:

.. rst-class:: tag-card

Tabs ``:tabs:`` ``:tab:``
-------------------------

A group of tabs, and one tab of the group. A ``:tabs:`` block holds only
``:tab:`` blocks, and cannot sit inside another ``:tabs:``. Each ``:tab:``
needs a ``:title:``, which names it in the row of tabs, and can hold any
blocks except proof steps. Blocks inside the tabs keep their own numbers. A
reference to a tab's label reads as its title.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :tabs:

     :tab: {:title: <title>}
       <blocks>
     ::

     :tab: {:title: <title>}
       <blocks>
     ::

   ::

.. rubric:: Meta keys

``:title:``
   On ``:tab:``, the name of the tab.

.. rubric:: Example

.. rsm::

   :theorem: {:label: thm-sq}
   The square of an odd number is odd.
   ::

   :tabs:

     :tab: {:title: Sketch}
       :sketch:
       Expand $(2k+1)^2$.
       ::
     ::

     :tab: {:title: Proof}
       :proof: {:of: thm-sq}
       If $n = 2k + 1$, then $n^2 = 2(2k^2 + 2k) + 1$. :qed:
       ::
     ::

   ::

.. rubric:: Related

:ref:`Proof <tag-proof>`, :ref:`Sketch <tag-sketch>`.
