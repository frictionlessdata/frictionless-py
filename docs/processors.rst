Processors
==========

Good Tables ships with a set of core processor classes.

All processors can be used as standalone processors, as well as being part of a pipeline.

StructureProcessor
------------------

Validates the data structure conforms to expectations for rows and columns.


SchemaProcessor
---------------

Validates the data against a JSON Table Schema.

If no schema is passed, optionally creates a schema from the data.


Custom
------

When working with Good Tables as a library, it is possible to call custom processors in your pipeline.

We have the start of some documentation of this in the Tutorials section.

A better entry point now may be to see the existing processors and use those as a starting point for implementing your own.
