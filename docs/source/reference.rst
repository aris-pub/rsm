.. _reference:

Reference
=========

Lookup-oriented documentation for RSM syntax, configuration, CLI, and API.

Language
********

.. toctree::
   :maxdepth: 1

   reference/syntax
   reference/special
   reference/configuration
   reference/tags
   reference/cli-commands
   reference/import-export

API Reference
*************

.. currentmodule:: rsm

Core modules implementing each step in the file processing pipeline:

.. autosummary::
   :toctree: reference
   :caption: Core Modules

   nodes
   reader
   tsparser
   transformer
   translator
   builder
   writer

User-facing modules:

.. autosummary::
   :toctree: reference
   :caption: User-facing modules

   app
   cli
   rsmlogger
