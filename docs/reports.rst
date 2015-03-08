Reports
=======

The results of any validation run, either by a standalone validator, or a pipeline, are written to a report.

Each validator writes to a `tellme.Report` instance (See the `TellMe`_ library for more information on its API).

Reports can then be generated in a variety of output formats supported by `TellMe`_.

Pipeline reports
----------------

In a pipeline, the `pipeline.Pipeline` class collects the reports from each validator into a `self.report` dictionary.

Additional calculations are performed for a summary, and this dictionary is returned as the report object.

So, a pipeline report will have a structure as follows:

::

    {
        'success': True,
        'summary': {#summary},
        'validator_one_name': {#summary}, {#results},
        'validator_two_name': {#summary}, {#results}
        # and so on
    }

Validator report schema
-----------------------

Each validator produces a report. The report's dict representation has two top-level keys: `summary` and `results`.

* `summary` provides a summary of the report.
* `results` is a list of result dicts, each of which conforms to a schema as described:

::

    {
        'result_type': '# type of this result',
        'result_category': '# category of this result (row/header)',
        'result_level': '# level of this result (info/warning/error)',
        'result_message': '# message of this result',
        'row_index': '# index of the row',
        'row_name': # 'headers' or valud of id or _id if present, or empty
        'row_position': '# index of the column (can be None)',
        'item_name': '# name of the cell (can be None)',
    }

Report summary schema
---------------------

::
    {
        'message': '# a summary message',
        'total_rows': # int,
        'total_columns': # int,
        'bad_rows': # int,
        'bad_columns': # int,
        'columns': [# list of dicts with position, name, type conformance (%) per column]
    }


.. _`TellMe`: https://github.com/okfn/tellme
