.. _configuration:

Configuration
=============

The ``:config:`` tag allows you to specify document-level settings that control how your
manuscript is rendered. Configuration settings are document properties that travel with
the ``.rsm`` file — if you share the file, it renders the same way for everyone.

Basic usage
***********

The ``:config:`` tag appears once per document and contains meta keys that define
document properties:

.. code-block:: text

   # My Document

   :config: {
     :accent: purple
     :typography: serif
     :lang: es
     :numbering: document
   }
   ::

   Content goes here.

The ``:config:`` tag can appear anywhere in the document, but by convention it is placed
near the top, after the title.

Available meta keys
*******************


:accent:
--------

Sets the accent color used throughout the document for links, interactive elements,
and highlights.

**Valid values:** ``blue`` (default), ``purple``, ``red``, ``green``, ``orange``,
``yellow``, ``pink``, ``gray``

**Example:**

.. code-block:: text

   :config: {
     :accent: purple
   }
   ::

All accent colors meet WCAG 2.1 Level AA accessibility requirements for color contrast
in both light and dark themes.


:typography:
------------

Sets the typeface style for the document.

**Valid values:**

- ``sans-serif`` (default) — Montserrat for headings, Source Sans 3 for body text
- ``serif`` — Source Serif 4 for both headings and body text

**Example:**

.. code-block:: text

   :config: {
     :typography: serif
   }
   ::


:lang:
------

Sets the document language. This affects screen reader pronunciation and appears in the
HTML ``lang`` attribute.

**Valid values:** Any valid language code following ISO 639-1 (2-letter) or ISO 639-2
(3-letter) format, optionally with a region code.

**Examples:**

- ``en`` (English, default)
- ``es`` (Spanish)
- ``fr`` (French)
- ``de`` (German)
- ``en-US`` (English, United States)
- ``zh-CN`` (Chinese, China)

**Example:**

.. code-block:: text

   :config: {
     :lang: es
   }
   ::


:numbering:
-----------

Controls how theorems, lemmas, and other numbered environments are numbered.

**Valid values:**

- ``section`` (default) — Numbers reset at each section (e.g., Theorem 1.1, Theorem 2.1)
- ``document`` — Numbers increment throughout the document (e.g., Theorem 1, Theorem 2)
- ``none`` — No automatic numbering

**Example:**

.. code-block:: text

   :config: {
     :numbering: document
   }
   ::


:toc-depth:
-----------

Sets how many heading levels appear in the table of contents.

**Valid values:** Integer from 1 to 6

**Example:**

.. code-block:: text

   :config: {
     :toc-depth: 3
   }
   ::

This will include h1, h2, and h3 headings in the table of contents.


:override-date:
---------------

Overrides the document's publication date. Accepts dates in ISO 8601 format.

**Example:**

.. code-block:: text

   :config: {
     :override-date: 2026-02-08
   }
   ::

Combining settings
******************

Multiple configuration keys can be combined in a single ``:config:`` block:

.. code-block:: text

   :config: {
     :accent: purple
     :typography: serif
     :lang: es
     :numbering: document
     :toc-depth: 2
   }
   ::

Notes
*****

- Only one ``:config:`` block is allowed per document. Multiple blocks will cause an error.
- All configuration keys are optional. Omitted keys use their default values.
- Invalid values (e.g., ``accent: hotpink``) will cause a parser error with a helpful message.
- Configuration is separate from build-time CLI flags (like ``--output`` or ``--standalone``),
  which control how the document is built rather than how it's presented.
