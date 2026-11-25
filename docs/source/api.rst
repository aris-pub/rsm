.. _python-api:

Python API
==========

The Python modules of RSM, for programs that build, check or convert RSM
documents. :ref:`how-rsm-works` explains what each step of the pipeline does.

.. currentmodule:: rsm

The modules of the pipeline, one for each step:

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

The modules for programs that use RSM:

.. autosummary::
   :toctree: reference
   :caption: User-facing modules

   app
   cli
   rsmlogger
