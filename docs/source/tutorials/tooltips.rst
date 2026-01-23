.. _tooltips:

References and tooltips
=======================

Use the ``:label:`` tag to assign a unique label to any part of the manuscript, and use
the ``:ref:`` tag to refer to it.

.. rsm::

   :remark: {
     :label: lbl1
   }
   This remark can be referenced by using
   its label.
   ::

   Refer to :ref:lbl1:: above.

Hovering over the link text will display a tooltip showing the referenced region.

By default, the ``:ref:`` tag is displayed using the type of region referenced and its
number, if it has one; this generates the text "Remark 1" in the preceding example.  You
can override this behavior when using the ``:reftext:`` tag.

.. rsm::

   :remark: {
     :label: lbl2
     :reftext: Awesome Remark
   }
   This remark can be referenced by using
   its label.
   ::

   Refer to :ref:lbl2:: above.

The ``:reftext:`` tag is used at the same place where the ``:label:`` tag is defined,
and it changes the default text displayed whenever the annotated region is referenced.
You can also override the behavior of a single call to ``:ref:`` by using the following
notation.

.. rsm::

   :remark: {
     :label: lbl3
   }
   This remark can be referenced by using
   its label.
   ::

   Refer to :ref:lbl3:: above, or call
   it :ref:lbl3, Awesome Remark::.

.. admonition:: Summary

   Use ``:label: <label>`` to assign a unique label to a region of the manuscript.  Use
   ``:ref:<label>::`` to reference a region via its label.  Override the displayed text
   globally by using ``:reftext: <text>`` at the location where the label is defined, or
   by using ``:ref:<label>,<text>::`` where the reference is used.  Regardless of the
   displayed text, a reference will display with a tooltip.
