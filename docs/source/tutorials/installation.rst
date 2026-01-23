.. _installation:

Installation
============

The package name is :code:`rsm-lang` and is available via pypi,

.. code-block:: bash

   $ pip install rsm-lang


Or, if you are using uv and already have a :code:`pyproject.toml` file:

.. code-block:: bash

   $ uv add rsm-lang



.. _checking-your-install:

Checking your install
---------------------
To test whether the installation was successful you may execute

.. code-block:: bash

   $ rsm render --version

If you want to use RSM from a python script, you may import the library with

.. code-block:: python

   import rsm

.. tip::

   The command

   .. code-block:: bash

      $ rsm render manuscript.rsm

   is essentially equivalent to the following code

   .. code-block:: python

      import rsm
      with open("manuscript.rsm") as f:
          src = f.read()
      print(rsm.render(src))
