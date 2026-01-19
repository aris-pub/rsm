.. _cli-commands:

CLI Commands
============

RSM provides three command line utilities when installed locally:

1. ``rsm build`` Takes a file containing RSM source and outputs a fully functioning
   website.2
. ``rsm render`` Takes a file containing RSM source and translates it to HTML.  It does
   not make a working website, it only computes the HTML body and prints it to screen.
3. ``rsm check`` Takes a file containing RSM source and runs consistency and sanity
   checks.  It outputs a set of warnings and suggestions to screen.  It does not write
   any HTML, and it does not overwrite the source file.

These three commands correspond one-to-one to the functions in the main package:
``rsm.build()``, ``rsm.render()``, and ``rsm.lint()``.

Most users will spend most of their time running ``rsm build``. The purpose of ``rsm
check`` is to be integrated to text editors in the future. ``rsm render`` is mostly
useful for development, testing, and rapid iteration at the CLI or python REPL.


Arguments and flags
*******************

We focus on the CLI flags accepted by ``rsm build``. The other two commands have very
similar flags. For a complete and updated list of arguments, run ``rsm build -h`` at
your terminal. Here we provide some common examples.

Suppose you have a file called ``manuscript.rsm`` containing RSM source code.  The
simplest way of building your web manuscript is via:

.. code-block:: bash

   $ rsm build manuscript.rsm

This will output a ``index.html`` file in the current directory, as well as a
``static/`` folder containing all necessary assets.


Input
-----

By default, ``rsm build`` interprets its first argument as a path to a file. You may
also provide RSM source directly at the terminal via the ``-c`` flag:

.. code-block:: bash

   $ rsm build ":rsm: Hello. ::" -c


Automatic builds
----------------

Using the ``--serve`` flag you may specify a path to ``rsm build`` and instruct it to
watch the file for any modifications. ``rsm build`` will rebuild the entire manuscript
whenever there is a change in the file, without you having to manually relaunch the
command.

.. code-block:: bash

   $ rsm build manuscript.rsm --serve
   [server] Serving on http://127.0.0.1:5500
   [handlers]Start watching changes
   [handlers]Start detecting changes
   ...


You may now open your browser at the address ``http://127.0.0.1:5500`` and see your
manuscript.  Whenever the ``manuscript.rsm`` file changes on disk, the browser will
automatically reload and show the changes.


Output
------

Sometimes it is useful to run the build without producing any output, just to see the
logs. This is possible with the ``-s`` flag. This is specially useful with ``rsm
render`` and ``rsm check``.


Logs
----

There are three flags to control the logs.

1. ``-v`` or ``-vv`` to control the verbosity.
2. ``--log-no-timestamps`` to remove timestamps from logs (useful during testing).
3. ``--log-format`` to change the format of the logs. The default value is ``"rsm"`` and
   it is most readable by humans. ``"json"`` is useful when transferring the logs to
   another application such as the online editor. ``"lint"`` is the format used by
   default by ``rsm check`` and it adheres to the same format used by other static
   analysis tools such as ``pylint`` and ``mypy``. ``"plain"`` is useful during testing.


Misc.
-----

1. ``rsm render`` accepts another flag, ``-r`` which uses the translator that outputs
   handrails (see :ref:`translator`).
2. ``rsm check`` ignores ``-s`` since by default it has no output other than logs.
3. ``rsm check`` ignores ``-v`` and ``-vv`` since it sets its own specific loglevel.
4. ``rsm check`` ignores ``-r`` since it never reaches the translation step.
5. ``rsm check`` and ``rsm render`` do not accept ``--serve``.
