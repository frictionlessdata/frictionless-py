Welcome to Tabular Validator's documentation!
=============================================

Tabular Validator is a pipeline interface for validating tabular data.

A **data source** is passed through a pipeline of **validators**.

Optionally, the data source is **transformed** as it passes through the pipeline.

In return, the client receives a **report** on validations performed.


Design goals
============

High-level design goals for Tabular Validator:

* Validate tabular data in CSV and JSON formats
* Provide a suite of small tools that each implement a type of validation to run
* Provide a pipeline API for registering built-in and custom validators
* Components should be easily usable in 3rd party (Python) code


Current status
==============

The suite of tools is current under development.


Get involved
============

You can contribute to the project with content, code, and ideas!

Start at one of the following channels:

`Mailing list`_: Discussion takes place on the openspending-dev mailing list

`IRC channel_`: We also have discussions on #openspending-dev at Freenode

`Documentation`_: An overview of the features that are currently in place.

`Issues`_: See current issues, the backlog, and/or file a new issue

`Code`_: Get the code here.


Table of contents
=================

.. toctree::
   :maxdepth: 2

   quickstart
   tutorial
   validators
   pipeline
   cli
   web


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _`Mailing list`: openspending-dev@lists.okfn.org
.. _`IRC channel`: #openspending
.. _`Documentation`: http://tabular-validator.readthedocs.org/
.. _`Issues`: https://github.com/okfn/tabular-validator/issues
.. _`Code`: https://github.com/okfn/tabular-validator
