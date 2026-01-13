.. _first-manuscript:

Your first manuscript
=====================

Create a new file called :code:`manuscript.rsm` and add the following contents

.. code-block:: text

   :rsm:

   Web-first scientific publishing.

   ::

In the command line, :code:`cd` to the directory where the :code:`manuscript.rsm` file
is stored and execute

.. code-block:: bash

   $ rsm-build manuscript.rsm

This will create a new file called :code:`index.html` in the same directory.  Open this
file with your web browser to see the web manuscript created by RSM.

RSM provides a linter as a command line utility.  Run the following command to see what
the linter suggests.

.. code-block:: bash

   $ rsm-lint manuscript.rsm
   src:1:12: LINT: Manuscript with no title

Here, the linter is telling us that our manuscript is missing a title.  We can rectify
that by editing :code:`manuscript.rsm` as follows

.. code-block:: text

   :rsm:
     :title: ReStructured Manuscripts

   Web-first scientific publishing.

   ::

Run again the ``rsm-lint`` command, and the warning should have disappeared.  You can
now run ``rsm-build`` again and refresh your browser to see now the title of your
manuscript displayed.
