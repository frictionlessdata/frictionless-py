Welcome to Good Tables's documentation!
=============================================

Good Tables is a pipeline interface for processing tabular data.

**data** (currently: as CSV and Excel) is passed through a pipeline of **processors**.

Optionally, the data source is **transformed** as it passes through the pipeline.

In return, the client receives a **report** on processing performed.


Design goals
============

High-level design goals for Good Tables:

* Process tabular data in CSV, Excel and JSON formats
* Provide a suite of small tools that each implement a type of processing to run
* Provide a pipeline API for registering built-in and custom processors
* Components should be easily usable in 3rd party (Python) code


Current status
==============

The suite of tools is current under development.


Get involved
============

You can contribute to the project with content, code, and ideas!

Start at one of the following channels:

`Mailing list`_: Discussion takes place on the openspending-dev mailing list.

`IRC channel`_: We also have discussions on #openspending-dev at Freenode.

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


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _`Mailing list`: openspending-dev@lists.okfn.org
.. _`IRC channel`: #openspending
.. _`Documentation`: http://goodtables.readthedocs.org/
.. _`Issues`: https://github.com/okfn/goodtables/issues
.. _`Code`: https://github.com/okfn/goodtables
