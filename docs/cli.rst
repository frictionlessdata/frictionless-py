CLI
===

Good Tables includes a command line interface, `goodtables`.

Pipeline
--------

Run a Good Tables pipeline.

Example
*******

::

    goodtables pipeline *data_source* --schema filepath_or_url --fail_fast --dry_run --row_limit 20000 --report_limit 1000


StructureProcessor
------------------

Run the Good Tables StructureProcessor.

Example
*******

::

    goodtables structure *data_source* --fail_fast --row_limit 20000 --report_limit 1000



SchemaProcessor
---------------

Run the Good Tables SchemaProcessor.

Example
*******

::

    goodtables schema *data_source* --schema filepath_or_url --fail_fast --row_limit 20000 --report_limit 1000
