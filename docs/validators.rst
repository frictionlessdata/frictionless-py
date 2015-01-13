Validators
==========

Structure
---------

Validates the data structure conforms to expectations for rows and columns.


Spec
----

Validates any specification files passed in with the data.

Currently supports the following specification formats:

* JSON Table Schema
* CSV Dialect
* Data Package


Schema
------

Validates the data against a JSON Table Schema.

If no schema is passed, optionally creates a schema from the data.


Probe
-----

TBD


Custom
------

It is easy to write your own custom validators. See the Tutorial for an example.
