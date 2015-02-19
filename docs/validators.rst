Validators
==========

Tabular Validator ships with a set of core validator classes.

All validators can be used as standalone validators, as well as being part of a validation pipeline.

StructureValidator
------------------

Validates the data structure conforms to expectations for rows and columns.


SchemaValidator
---------------

Validates the data against a JSON Table Schema.

If no schema is passed, optionally creates a schema from the data.


Custom
------

When working with Tabular Validator as a library, it is possible to call custom validators in your pipeline.

We have the start of some documentation of this in the Tutorials section.

A better entry point now may be to see the existing validators and use those as a starting point for implementing your own.
