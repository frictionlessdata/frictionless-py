Pipeline
========

Naturally, the `pipeline.Pipeline` class implements the processing pipeline.

Processor registration
**********************

Register by constructor
+++++++++++++++++++++++

The `pipeline.Pipeline` constructor takes a `processors` keyword argument, which is a list of processors to run in the pipeline.

Each value in the `processors` list is expected to be a string describing the path to a processor class, for import via `importlib`.

Optionally, for builtin processors, the `processor.name` property can be used as a shorthand convenience.

**Example**
::
    processors = ['structure', 'schema']  # short hand names for builtin processors
    processors = ['my_module.CustomProcessorOne', 'my_module.CustomProcessorTwo']  # import from string
    processors = ['structure', 'my_module.CustomProcessorTwo']  # both combined

Register by instance method
+++++++++++++++++++++++++++

Once you have a `pipeline.Pipeline` instance, you can also register processors via the `register_processor` method.

Registering new processors this way will by default append the new processors to any existing pipeline.

You can define the position in the pipeline explicitly using the `position` argument.

**Example**
::
    pipeline = Pipeline(args, kwargs)
    pipeline.register_processor('structure', structure_options)
    pipeline.register_processor('spec', spec_options, 0)

Processor options
*****************

`Pipeline` takes an `options` keyword argument to pass options into each processor in the pipeline.

`options` should be a dict, with each top-level key being the name of the processor.

**Example**
::
    pipeline_options = {
        'structure': {
            # keyword args for the StructureProcessor
        },
        'schema': {
            # keyword args for the SchemaProcessor
        }
    }

Instantiating the pipeline
**************************

**WIP**

TODO: This is not complete

Running the pipeline
********************

Run the pipeline with the `run` method.

`run` in turn calls the supported **processor methods** of each processor.

Once the data table has been run through all processors, `run` returns a tuple of `valid, report`, where:

* `valid` is a boolean, indicating if the data table is valid according to the pipeline validation
* `report` is `tellme.Report` instance, which can be used to generate a report in various formats


Processor arguments
*******************

Most processors will have custom keyword arguments for their configuration.

Additionally, all processors are expected to take the following keyword arguments, and exhibit certain behaviour based on their values.

The `base.Processor` signature implements these arguments.

`fail_fast`
+++++++++++

`fail_fast` is a boolean that defaults to `False`.

If `fail_fast` is `True`, the processor is expected to stop processing as soon as an error occurs.

`transform`
+++++++++++

`transform` is a boolean that defaults to `True`.

If `transform` is `True`, then the processor is "allowed" to return transformed data.

The caller (e.g., the pipeline class) is responsible for persisting transformed data.

`report_limit`
++++++++++++++

`report_limit` is an int that defaults to `1000`, and refers to the maximum amount of entries that this processor can write to a report.

If this number is reached, the processor should stop processing.

`row_limit`
+++++++++++

`row_limit` is an int that defaults to `20000`, and refers to the maximum amount of rows that this processor will process.

`report_stream`
+++++++++++++++

`report_stream` allows calling code to pass in a writable, seekable text stream to write report entries to.


Processor attributes
********************

Processors are also expected to have the following attributes.

`report`
++++++++

A `tellme.Report` instance. See `TellMe`_

Processors are expected to write report entries to the report instance.

`pipeline.Pipeline` will call `processor.report.generate` for each processor to build the pipeline report.

`name`
++++++

A shorthand name for this processor. `name` should be unique when called in a pipeline.

Processors that inherit from `base.Processor` have a name that defaults to a lower-cased version of the class name.


.. _`TellMe`: https://github.com/okfn/tellme
