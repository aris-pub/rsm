.. _latex-mental-model:

RSM for LaTeX Users
===================

If you already know LaTeX, most RSM concepts have direct equivalents. This
page maps LaTeX thinking to RSM thinking.


Document structure
------------------

.. list-table::
   :header-rows: 1
   :widths: 40 40

   * - LaTeX
     - RSM
   * - ``\documentclass{article}``
     - Not needed. RSM has one document type.
   * - ``\title{...}``
     - ``# Title``
   * - ``\author{...}``
     - ``:author: {:name: ... :affiliation: ...} ::``
   * - ``\begin{abstract}...\end{abstract}``
     - ``:abstract: ... ::``
   * - ``\section{...}``
     - ``## Heading``
   * - ``\subsection{...}``
     - ``### Heading``
   * - ``\appendix``
     - ``:appendix:``
   * - ``\bibliography{refs}``
     - ``:references: ... ::`` (inline BibTeX entries)


Environments
------------

.. list-table::
   :header-rows: 1
   :widths: 40 40

   * - LaTeX
     - RSM
   * - ``\begin{theorem}...\end{theorem}``
     - ``:theorem: ... ::``
   * - ``\begin{proof}...\end{proof}``
     - ``:proof: ... ::``
   * - ``\begin{definition}...\end{definition}``
     - ``:definition: ... ::``
   * - ``\begin{lemma}...\end{lemma}``
     - ``:lemma: ... ::``
   * - ``\begin{enumerate}...\end{enumerate}``
     - ``:enumerate: :-: item :-: item ::``
   * - ``\begin{figure}...\end{figure}``
     - ``:figure: {:path: img.png} ::``
   * - ``\begin{equation}...\end{equation}``
     - ``:mathblock: ... ::`` or ``$$ ... $$``


Inline commands
---------------

.. list-table::
   :header-rows: 1
   :widths: 40 40

   * - LaTeX
     - RSM
   * - ``\textbf{bold}``
     - ``**bold**``
   * - ``\textit{italic}``
     - ``*italic*``
   * - ``$x^2$``
     - ``$x^2$``
   * - ``\cite{key}``
     - ``:cite:key::``
   * - ``\ref{label}``
     - ``:ref:label::``
   * - ``\label{name}``
     - ``:label: name`` (as a meta tag)
   * - ``\verb|code|``
     - `````code````` or ``:code:code::``


Key differences
---------------

**No preamble.**
RSM has no equivalent of ``\usepackage`` or preamble configuration.
Document-level settings use ``:config: {:accent: blue :numbering: section} ::``.

**No compilation.**
``rsm build`` produces HTML directly. No ``.aux`` files, no multiple passes,
no BibTeX/biber step. Citations resolve in a single build.

**Tags close with Halmos.**
Every RSM tag ends with ``::`` (the Halmos). This replaces LaTeX's
``\end{environment}`` and closing braces. It takes a few minutes to get used
to, then it becomes natural.

**Semantic, not visual.**
LaTeX mixes semantics and presentation (``\textbf`` is visual,
``\begin{theorem}`` is semantic). In RSM, all tags are semantic. Presentation
is handled by the BRAIID design system.

**The output is HTML, not PDF.**
RSM produces responsive, interactive web documents. If you need PDF, RSM can
export via Pandoc/Typst, but the primary target is the browser.
