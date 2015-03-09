Reports
=======

The results of any run over data, either by a standalone processor or a pipeline, are written to a report.

Each report is an instance of a `tellme.Report`, which is a small library we also developed (See the `TellMe`_ library for more information on its API).

Reports can then be generated in a variety of output formats supported by `TellMe`_.

Pipeline reports
----------------

In a pipeline, the `pipeline.Pipeline` each processor writes report results to the pipeline's report instance.

After processing of the data is complete, additional calculations are performed for a summary.

Finally, the report is generated to an output format (a Python dict in this case) and returned.

From a top-level view, a pipeline report will have the following structure:

::

    {
        'success': True,
        'meta': {'name': 'Pipeline'},
        'summary': {#summary},
        'results': [...]
    }

All the interesting stuff is happening in the results array and the sumamry object.

See below for a description of each object in the results array, and likewise a description of the summary object.

Standalone processor reports
----------------------------

Standalone processors (for example, the built-in `StructureProcessor`) have a report object almost identical to that of a pipeline report, except they do not have a summary object.

Report result schema
--------------------

::

    {
        'result_type': '# type of this result',
        'result_category': '# category of this result (row/header)',
        'result_level': '# level of this result (info/warning/error)',
        'result_message': '# message of this result',
        'result_context': [# a list of the values of the row that the result was generated from]
        'row_index': '# index of the row',
        'row_name': # 'headers' or valud of id or _id if present, or empty
        'column_index': '# index of the column (can be None)',
        'column_name': '# name of the column (can be '')',
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
