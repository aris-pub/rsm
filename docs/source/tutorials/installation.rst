.. _installation:

Installation
============

The package name is :code:`rsm-markup` and is available via pypi,

.. code-block:: bash

   $ pip install rsm-markup


Or, if you are using poetry and you already have a :code:`pyproject.toml` file in the
current directory:

.. code-block:: bash

   $ poetry add rsm-markup



.. _checking-your-install:

Checking your install
---------------------

.. tip::
   :class: sidebar

   The command

   .. code-block:: bash

      $ rsm-render manuscript.rsm

   is essentially equivalent to the following code

   .. code-block:: python

      import rsm
      with open("manuscript.rsm") as f:
          src = f.read()
      print(rsm.render(src))

.. grid:: 1 1 1 1

   .. grid-item::

      To test whether the installation was successful you may execute

      .. code-block:: bash

         $ rsm-render --version

      If you want to use RSM from a python script, you may import the library with

      .. code-block:: python

         import rsm
