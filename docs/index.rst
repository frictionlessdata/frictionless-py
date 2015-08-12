Welcome to Good Tables's documentation!
=============================================

Good Tables is a python library and command line tool for validating and transforming tabular data.

**Tabular data** in the form of CSV or Excel is passed through a pipeline of **validators**. These validators can **check structure**, for example are their blank rows or columns, do rows have the same length as the header etc, and they can also **validate against a schema**, for example does the data have the expected columns, is the data of the right type (are dates actually dates).

Optionally, the data source is **transformed** as it passes through the pipeline.

In return, the client receives a **report** on processing performed and, optionally, the output data.

Get involved
============

You can contribute to the project with content, code, and ideas!

Start at one of the following channels:

`Documentation`_: An overview of the features that are currently in place.

`Issues`_: See current issues, the backlog, and/or file a new issue.

`Code`_: Get the code here.

Table of contents
=================

.. toctree::
   :maxdepth: 2

   quickstart
   tutorial
   validators
   pipeline
   batch
   reports
   cli

Design goals
============

High-level design goals for Good Tables:

* Process tabular data in CSV, Excel and JSON formats
* Provide a suite of small tools that each implement a type of processing to run
* Provide a pipeline API for registering built-in and custom processors
* Components should be easily usable in 3rd party (Python) code

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _`Documentation`: http://goodtables.readthedocs.org/
.. _`Issues`: https://github.com/okfn/goodtables/issues
.. _`Code`: https://github.com/okfn/goodtables
