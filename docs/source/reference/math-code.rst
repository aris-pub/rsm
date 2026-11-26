.. _ref-math-code:

Math and code
=============

Math is written in LaTeX and shown with MathJax. Displayed equations are
numbered within their section, such as (2.1), and a reference to one reads
"(2.1)". Algorithms are also numbered within their section, and a reference
to one reads "Algorithm 2.1". Code blocks are numbered within their section
too, with their own counter, and a reference to one reads "Code Block 2.1".

Every tag on this page takes the meta keys that all tags take, such as
``:label:`` and ``:nonum:``. See :ref:`ref-meta-keys`.


.. _tag-math:

.. rst-class:: tag-card

Inline math ``$`` ``:math:``
----------------------------

Math inside a line of text. ``$...$`` and ``:math:...::`` are the same.

.. rubric:: Syntax

.. rsm::
   :source-only:

   Text with $<latex>$ in it.

.. rubric:: Related

:ref:`Displayed math <tag-mathblock>`, :ref:`Notation <tag-notation>`.


.. _tag-mathblock:

.. rst-class:: tag-card

Displayed math ``$$`` ``:mathblock:``
-------------------------------------

An equation on its own lines, numbered. ``$$`` on a line of its own starts it
and another ``$$`` ends it. With no blank line before or after it, the
equation belongs to the paragraph around it. Meta keys go in braces after the
opening ``$$``. ``:mathblock: ... ::`` is the same.

.. rubric:: Syntax

.. rsm::
   :source-only:

   $$ {:label: <label>}
   <latex>
   $$

.. rubric:: Meta keys

``:preamble:``
   Hides the block and runs it before all other math, so that LaTeX
   definitions in it, such as ``\newcommand``, apply to the whole document.
   The block is not numbered.

``:isclaim:``
   Makes the equation the claim of the proof step that it is in, as
   ``:claim:`` does for text.

.. rubric:: Example

.. rsm::

   $$ {:preamble:}
   \newcommand{\R}{\mathbb{R}}
   $$

   For every $x \in \R$,
   $$ {:label: eq-sq}
   x^2 \geq 0.
   $$
   We use :ref:eq-sq:: below.

.. rubric:: Related

:ref:`Inline math <tag-math>`, :ref:`Calculation <tag-calc>`.


.. _tag-notation:

.. rst-class:: tag-card

Notation ``:notation:``
-----------------------

LaTeX macros for the symbols of the document, one per line, each with its
default form and a name. The reader can change how each symbol is shown, in
the notation panel of the sidebar. The block itself shows nothing in the
page.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :notation:
     \<macro> $<default latex>$ <name>
   ::

.. rubric:: Example

.. rsm::

   :notation:
     \eig $\lambda$ eigenvalue
   ::

   Every $\eig$ of a symmetric matrix is real.

.. rubric:: Related

:ref:`Inline math <tag-math>`, :ref:`reading-sidebar`.


.. _tag-code:

.. rst-class:: tag-card

Inline code :literal:`\`` ``:code:``
------------------------------------

Code inside a line of text, in a fixed-width font. Code between backticks
and ``:code:...::`` are the same. ``:code:`` takes a language for syntax
colors.

.. rubric:: Syntax

.. rsm::
   :source-only:

   Run :code: {:lang: python} print(1) :: in a terminal.

.. rubric:: Meta keys

``:lang:``
   The language of the code, such as ``python``.

.. rubric:: Related

:ref:`Code block <tag-codeblock>`.


.. _tag-codeblock:

.. rst-class:: tag-card

Code block ``:codeblock:``
--------------------------

Lines of code, in a fixed-width font, with syntax colors for the language in
``:lang:``. The lines are shown as written.

Code blocks are numbered within their section, such as Code Block 2.1, with
their own counter. A reference to one reads "Code Block 2.1", or its
``:reftext:``. A code block can end with a ``:caption:`` on a line of its own,
after the code. RSM shows the caption under the block, with the label "Code
Block 2.1." before it, or in the margin column when the page is wide enough. A
code block without a caption shows no label. A block that is written between
two lines of three backticks is numbered the same way but takes no caption.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :codeblock: {:lang: python}
   <code>
   :caption: <caption>
   ::

.. rubric:: Meta keys

``:lang:``
   The language of the code, such as ``python``.

``:blockname:``
   A name that replaces "Code Block" in the block's label and in references
   to it, such as ``Listing``.

.. rubric:: Example

.. rsm::

   :codeblock: {:lang: python, :label: code-square}
   def square(x):
       return x * x
   :caption: The square of a number.
   ::

   :ref:code-square:: returns the square of its argument.

.. rubric:: Related

:ref:`Inline code <tag-code>`, :ref:`Algorithm <tag-algorithm>`,
:ref:`Caption <tag-caption>`.


.. _tag-algorithm:

.. rst-class:: tag-card

Algorithm ``:algorithm:``
-------------------------

Pseudocode, written with the LaTeX ``algorithmic`` commands and shown with
`pseudocode.js <https://saswat.padhi.me/pseudocode.js/>`_. The content is
LaTeX, not RSM.

.. rubric:: Syntax

.. rsm::
   :source-only:

   :algorithm:
   \begin{algorithm}
   \caption{<name>}
   \begin{algorithmic}
   <commands>
   \end{algorithmic}
   \end{algorithm}
   ::

.. rubric:: Example

.. rsm::

   :algorithm:
   \begin{algorithm}
   \caption{Sum}
   \begin{algorithmic}
   \STATE $s = 0$
   \FOR{$i = 1$ \TO $n$}
       \STATE $s = s + i$
   \ENDFOR
   \end{algorithmic}
   \end{algorithm}
   ::

.. rubric:: Related

:ref:`Code block <tag-codeblock>`.
