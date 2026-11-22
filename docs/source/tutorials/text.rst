.. _tutorial-text:

Text, headings, lists and math
==============================

Most of a document is paragraphs, sections, lists, math and code. This lesson
goes through each of them.

.. rsm::

   # Notes on primes

   ## Definitions

   A prime is a whole number larger than 1
   that has no divisors other than 1 and itself.
   % This line is a comment and does not appear.

   The first primes are:

   :itemize:

     :-: 2, the only even prime,

     :--: which divides every even number,

     :-: 3, 5 and 7.

   ::

   ### Counting primes

   :enumerate:

     :-: Write the numbers from 2 to $n$.

     :-: Cross out the multiples of each prime.

   ::

   Euclid proved that there are infinitely many primes.
   The product of the first $k$ primes plus one is

   $$ {:label: eq-euclid}
   N = p_1 p_2 \cdots p_k + 1,
   $$

   and no $p_i$ divides $N$. Equation :ref:eq-euclid:: is
   the heart of the proof. In code, `is_prime(7)` returns `True`.


Paragraphs
----------

A blank line ends a paragraph. Lines with no blank line between them belong to
the same paragraph, so you can break lines wherever you like in the source.

A ``%`` starts a comment, which runs to the end of the line and does not
appear on the page.


Headings
--------

``#`` starts the title of the document. ``##`` starts a section, ``###`` a
subsection and ``####`` a subsubsection. RSM numbers them for you: 1, 1.1,
1.1.1.


Bold, italic and code
---------------------

``**bold**`` makes bold text, ``*italic*`` makes italic text, and
```code``` (in backticks) sets text in a fixed-width font.


Lists
-----

``:itemize:`` makes a list with bullets, and ``:enumerate:`` makes a numbered
list. Each item starts with ``:-:``, and items are separated by blank lines.
``:--:`` makes an item one level deeper, and ``:---:`` two levels deeper. The
list ends with ``::``.


Math
----

Math is written in LaTeX. ``$...$`` puts math inside a line of text. ``$$`` on
a line of its own starts a displayed equation, and another ``$$`` ends it.
RSM numbers displayed equations.

To refer to an equation later, give it a label in braces after the opening
``$$``, as with ``{:label: eq-euclid}`` above. ``:ref:eq-euclid::`` then turns
into the equation's number, as a link. See :ref:`tutorial-references` for
more on labels and references.


Special characters
------------------

A backslash makes the next character plain text: ``\$`` gives a dollar sign,
``\%`` a percent sign, and ``\::`` two colons.

The next lesson is :ref:`tutorial-theorems`.
