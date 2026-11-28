.. _latex-mental-model:

RSM for LaTeX users
===================

Most of what you write in LaTeX has a direct equivalent in RSM, and the math
is the same LaTeX. This page shows one paper in both languages, lists the
equivalents, and explains the few things that RSM does differently.


The same paper in LaTeX and in RSM
----------------------------------

In LaTeX:

.. code-block:: latex

   \documentclass{article}
   \usepackage{amsthm}
   \newtheorem{theorem}{Theorem}
   \title{Graphs without triangles}
   \author{Ada Lovelace \\ University of London}
   \begin{document}
   \maketitle
   \begin{abstract}
   We give a short proof of Mantel's theorem.
   \end{abstract}

   \section{Results}

   \begin{theorem}[Mantel]\label{thm:mantel}
   A graph with $n$ vertices and no triangle has at most $n^2/4$ edges.
   \end{theorem}

   \begin{proof}
   The two ends of an edge $uv$ have no common neighbor, so
   \begin{equation}\label{eq:sum}
   \sum_v d(v)^2 = \sum_{uv} \big(d(u) + d(v)\big) \le n e.
   \end{equation}
   By \eqref{eq:sum} and the Cauchy-Schwarz inequality, $e \le n^2/4$.
   \end{proof}

   \end{document}

In RSM:

.. rsm::

   # Graphs without triangles

   :author: {
     :name: Ada Lovelace
     :affiliation: University of London
   } ::

   :abstract:
   We give a short proof of Mantel's theorem.
   ::

   ## Results

   :theorem: {:label: thm-mantel, :title: Mantel}
   A graph with $n$ vertices and no triangle has at most $n^2/4$ edges.
   ::

   :proof: {:of: thm-mantel}
   The two ends of an edge $uv$ have no common neighbor, so
   $$ {:label: eq-sum}
   \sum_v d(v)^2 = \sum_{uv} \big(d(u) + d(v)\big) \le n e.
   $$
   By :ref:eq-sum:: and the Cauchy-Schwarz inequality, $e \le n^2/4$.
   ::

The RSM version has no preamble, a label is a meta key in braces instead of a
``\label`` command, and ``::`` ends each block.


Equivalents
-----------

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - LaTeX
     - RSM
   * - ``\title{...}``
     - ``# Title``
   * - ``\author{...}``
     - ``:author:``, with ``:name:``, ``:affiliation:``, ``:email:`` and
       ``:orcid:``. See :ref:`multi-author-guide`.
   * - ``\begin{abstract}``
     - ``:abstract:``
   * - ``\section``, ``\subsection``, ``\subsubsection``
     - ``##``, ``###``, ``####``
   * - ``\section*{...}``
     - ``## ... {:nonum:}``
   * - ``\appendix``
     - ``:appendix:``
   * - ``\begin{theorem}``, ``lemma``, ``proposition``, ``corollary``,
       ``definition``, ``remark``, ``example``
     - ``:theorem:``, ``:lemma:``, ``:proposition:``, ``:corollary:``,
       ``:definition:``, ``:remark:``, ``:example:``
   * - ``\newtheorem{claim}{Claim}``
     - ``:lemma: {:blockname: Claim}``
   * - ``\begin{theorem}[Mantel]``
     - ``:theorem: {:title: Mantel}``
   * - ``\begin{proof}``
     - ``:proof:``, and ``:proof: {:of: <label>}`` for "Proof of Theorem 1.1"
   * - ``\label{key}``
     - ``{:label: key}`` in the meta keys of the block
   * - ``\ref{key}``, ``\eqref{key}``
     - ``:ref:key::``. RSM writes "Theorem 1.1" or "(1.1)", so leave out the
       word "Theorem".
   * - ``\cite{key}``
     - ``:cite:key::``
   * - ``\bibliography{refs}`` and a ``.bib`` file
     - ``:references:`` with the BibTeX entries in it. See
       :ref:`guide-citations`.
   * - ``\begin{equation}``
     - ``$$`` on lines of their own, or ``:mathblock:``
   * - ``\[ ... \]``, ``equation*``
     - ``$$ {:nonum:}``
   * - ``\newcommand{\eig}{\lambda}``
     - ``:notation:``. See :ref:`guide-notation`.
   * - ``\begin{itemize}``, ``\begin{enumerate}``, ``\item``
     - ``:itemize:``, ``:enumerate:``, ``:-:``
   * - ``\begin{figure}``, ``\includegraphics``, ``\caption``
     - ``:figure: {:path: plot.png}`` with ``:caption:`` inside
   * - ``\begin{table}``, ``tabular``
     - ``:table:``, ``:tr:``
   * - ``\footnote{...}``
     - ``:note:``. See :ref:`guide-footnotes-asides`.
   * - ``\textbf{...}``, ``\emph{...}``
     - ``**...**``, ``*...*``
   * - ``\texttt{...}``
     - ```...```
   * - ``\href{url}{text}``, ``\url{url}``
     - ``:url:url, text::``, ``:url:url::``
   * - ``% comment``
     - ``% comment``

See :ref:`language-reference` for every tag.


What RSM does differently
-------------------------

**RSM numbers everything itself.** Sections, theorems, figures and equations
get their numbers from RSM, on the web page and in every export. ``:nonum:``
on a block leaves it unnumbered, and ``:numbering:`` in the ``:config:``
block numbers the blocks within each section (the default), through the whole
document, or not at all.

**LaTeX goes in math only, and only for typesetting.** Write the math in
LaTeX, but write the structure of the document with RSM tags: labels,
numbers, references, citations, sections, captions and footnotes. The build
stops with an error when math uses a LaTeX command for one of these, such as
``\label``, ``\tag``, ``\ref``, ``\cite`` or ``\section``, and the error says
what to write instead. Starred environments such as ``align*`` and
``equation*`` are not allowed either: write ``align`` or ``equation`` and put
``:nonum:`` on the block. See :ref:`tag-mathblock` for the whole list.

**There is no preamble.** Settings go in the ``:config:`` block, and macros
for the symbols of the paper go in ``:notation:``, where the reader can
change how each symbol is shown.

**There is one build.** ``rsm build`` writes the web page in one step, with
every reference and citation resolved. There are no ``.aux`` files and no
BibTeX step.

**A double colon ends a tag.** A block such as ``:theorem:`` ends with ``::`` on its
own line, as ``\end{theorem}`` ends an environment. An inline tag such as
``:ref:key::`` ends with ``::`` too. Headings and paragraphs need none.

**The output is a web page.** The reader can open proofs step by step, read
the statement of a result in a tooltip, and change the notation. For a
journal or a printed copy, export to LaTeX or PDF: see
:ref:`converting-guide`.


Bring a paper over from LaTeX
-----------------------------

``rsm import`` turns a LaTeX paper, or a folder or archive that holds a
LaTeX project, into RSM source:

.. code-block:: bash

   rsm import paper.tex --from latex -o paper.rsm

See :ref:`converting-guide` for what the import writes and what to check
afterwards.
