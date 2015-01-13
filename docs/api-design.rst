API Design
==========

The `ValidationPipeline` class implements the pipeline by calling validators in order.

Each Validator class is expected to conform to the following API in order to validate, transform and report correctly.


Validator methods
-----------------

`pre_run`
+++++++++

`run_row`
+++++++++

`run_column`
++++++++++++

`post_run`
++++++++++

`generate_reports`
++++++++++++++++++

`run`
+++++

`run` is **not** required for invocation via a validation pipeline.


Pipeline execution
------------------
