CLI
===

The library includes a command line interface.

Pipeline
--------

Command
*******

::

tv validate *data_source* --schema filepath_or_url --fail_fast --dry_run --row_limit 20000 --report_limit 1000

# or

python cli/main.py validate *data_source* --schema filepath_or_url --fail_fast --dry_run --row_limit 20000 --report_limit 1000

See the CLI tests for examples.
