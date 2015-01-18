CLI
===

The library includes a command line interface.

Pipeline
--------

Command
*******

::

tv pipeline *data_source*

# or

python cli/main.py pipeline *data_source*

Examples
********

Try it yourself on your own data, or the data in the `examples` directory.

::

tv pipeline examples/valid.csv

tv pipeline examples/defective_rows.csv

tv pipeline examples/duplicate_rows.csv

# etc.


Test
----

Command
*******

::

tv test

# or

python cli/main.py test

Run the project tests.

# TODO: Default discovery is not yet working via the CLI. Use this instead:

::

python -m unittest tests
