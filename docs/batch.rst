Batch
=====

`pipeline.Batch` Allows the configuration and running of pipelines on multiple sources.

Data sources can be extracted from either a CSV file, or a Data Package.

Arguments
---------

* `source`: Filepath to the lust of data sources to run the batch against.
* `source_type`: 'csv' (CSV file) or 'dp' (Data Package file).
* `data_key`: If `source_type` is 'csv', then this is the name of the header that indicates the data URL.
* `schema_key`: If `source_type` is 'csv', then this is the name of the header that indicates the schema URL.
* `pipeline_options`: The `options` keyword argument for the `pipeline.Pipeline` constructor.
* `post_task`: Any callable that takes the batch instance as its only argument. Runs after the batch processing is complete.
* `pipeline_post_task`: Any callable that takes a pipeline instance as its only argument. Runs on completion of each pipeline.

For an example of the batch processor at work, including use of `post_task` and `pipeline_post_task`, see `spd-admin`_.


.. _`spd-admin`: https://github.com/okfn/spd-admin
