Pipeline
========

Naturally, the `pipeline.Pipeline` class implements the processing pipeline.

Validator registration
**********************

Register by constructor
+++++++++++++++++++++++

The `pipeline.Pipeline` constructor takes a `validators` keyword argument, which is a list of validators to run in the pipeline.

Each value in the `validators` list is expected to be a string describing the path to a validator class, for import via `importlib`.

Optionally, for builtin validators, the `validator.name` property can be used as a shorthand convenience.

**Example**
::
    validators = ['structure', 'schema']  # short hand names for builtin validators
    validators = ['my_module.CustomValidatorOne', 'my_module.CustomValidatorTwo']  # import from string
    validators = ['structure', 'my_module.CustomValidatorTwo']  # both combined

Register by instance method
+++++++++++++++++++++++++++

Once you have a `pipeline.Pipeline` instance, you can also register validators via the `register_validator` method.

Registering new validators this way will by default append the new validators to any existing pipeline.

You can define the position in the pipeline explicitly using the `position` argument.

**Example**
::
    pipeline = Pipeline(args, kwargs)
    pipeline.register_validator('structure', structure_options)
    pipeline.register_validator('spec', spec_options, 0)

Validator options
*****************

`Pipeline` takes an `options` keyword argument to pass options into each validator in the pipeline.

`options` should be a dict, with each top-level key being the name of the validator.

**Example**
::
    pipeline_options = {
        'structure': {
            # keyword args for the StructureValidator
        },
        'schema': {
            # keyword args for the SchemaValidator
        }
    }

Instantiating the pipeline
**************************

**WIP**

TODO: This is not complete

Running the pipeline
********************

Run the pipeline with the `run` method.

`run` in turn calls the supported **validator methods** of each validator.

Once the data table has been run through all validators, `run` returns a tuple of `valid, report`, where:

* `valid` is a boolean, indicating if the data table is valid according to the pipeline validation
* `report` is `tellme.Report` instance, which can be used to generate a report in various formats


Validator arguments
*******************

Most validators will have custom keyword arguments for their configuration.

Additionally, all validators are expected to take the following keyword arguments, and exhibit certain behaviour based on their values.

The `base.Validator` signature implements these arguments.

`fail_fast`
+++++++++++

`fail_fast` is a boolean that defaults to `False`.

If `fail_fast` is `True`, the validator is expected to stop processing as soon as an error occurs.

`transform`
+++++++++++

`transform` is a boolean that defaults to `True`.

If `transform` is `True`, then the validator is "allowed" to return transformed data.

The caller (e.g., the pipeline class) is responsible for persisting transformed data.

`report_limit`
++++++++++++++

`report_limit` is an int that defaults to `1000`, and refers to the maximum amount of entries that this validator can write to a report.

If this number is reached, the validator should stop processing.

`row_limit`
+++++++++++

`row_limit` is an int that defaults to `20000`, and refers to the maximum amount of rows that this validator will process.

`report_stream`
+++++++++++++++

`report_stream` allows calling code to pass in a writable, seekable text stream to write report entries to.


Validator attributes
********************

Validators are also expected to have the following attributes.

`report`
++++++++

A `tellme.Report` instance. See `TellMe`_

Validators are expected to write report entries to the report instance.

`pipeline.Pipeline` will call `validator.report.generate` for each validator to build the pipeline report.

`name`
++++++

A shorthand name for this validator. `name` should be unique when called in a pipeline.

Validators that inherit from `base.Validator` have a name that defaults to a lower-cased version of the class name.


.. _`TellMe`: https://github.com/okfn/tellme
