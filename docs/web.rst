Web
===

Validation pipelines can be run over HTTP with Tabular Validator Web.

The Web library is designed to be used either as a standalone HTTP service (exposed via a *Flask app*), or, as a part of a larger Flask app (by using the API component as a *Flask blueprint*).

Spec
----

Endpoints
*********

The web API will expose the following endpoints.

Index [ / ]
+++++++++++

Get list of all available API endpoints as JSON, with description of what they do.

Also nice if it returns an HTML version if visited in browser.

Submit [ /submit/ ]
+++++++++++++++++++

POST data for submission.

Data would be meta data like user/department name, and all data and spec files.

**Return object**:

* Status (success of submit action)
* Job number (in initial non-queued implementation, will return the actual report as JSON, if success)

Submit Bulk [ /submit/bulk/ ]
+++++++++++++++++++++++++++++

POST data for bulk submission.

Data would be a CSV file (format TBD), where each row is data for submission.

**Return object**:

* Status (success of submit action)
* Job numbers (for each row)

Jobs [ /jobs/ ]
+++++++++++++++

GET a (paginated) list of jobs, ordered by submit date.

**Filters**:

* Date from
* Date to
* Job IDs (list)

**Return object**:

* ID (unique identifier for job)
* State (e.g.: queued/processing/completed)

Jobs [ /jobs/<ID>/ ]
++++++++++++++++++++

GET a detailed result on a given job

**Return object**:

* ID (unique identifier for job)
* State (e.g.: queued/processing/completed)
* Raw sources (list of objects, where each object is the passed in data and spec files for the job, i.e.: links to their persistent location)
* Data (link to the (probably transformed) data file)
* Report (object - the generated report, either inlined or a file ref.)

File persistence
****************

The web API *should* also provide a minimal implementation of file persistence, on top of an object storage backend (using Apache Libcloud, etc.).

Need to check about object storage and streaming data into files:

AFAIK S3 for example can't support streaming writes? So, might need a local cache to write to while working, and then copy finished files over.

Location
++++++++

Each Job can have a location (a directory) under the Job ID.

Source files
++++++++++++

Source files uploaded by the user go directly to the storage location.

Transformed source files
++++++++++++++++++++++++

Source data may be transformed in the pipeline. Resulting transformed files of 'normalized' data go to the storage location.

Report files
++++++++++++

Reports are generated in a file format, and saved to the storage location.

**To solve:**

* Subsequent jobs on same data - version pattern
