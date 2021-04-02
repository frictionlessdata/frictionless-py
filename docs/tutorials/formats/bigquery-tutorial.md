---
title: BugQuery Tutorial
sidebar_label: BigQuery
---

> This functionality requires an experimental `bigquery` plugin. [Read More](../../references/plugins-reference.md)

Frictionless supports both reading tables from BigQuery source and treating a BigQuery dataset as a tabular data storage.

```bash
pip install frictionless[bigquery]
```

## Reading Data

You can read from this source using `Package/Resource`, for example:

```python title="Python"
import os
import json
from pprint import pprint
from apiclient.discovery import build
from oauth2client.client import GoogleCredentials
from frictionless import Resource
from frictionless.plugins.bigquery import BigqueryDialect

# Prepare BigQuery
# This file can be received from Google Console
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ".google.json"
credentials = GoogleCredentials.get_application_default()
service = build("bigquery", "v2", credentials=credentials),
project = json.load(open(".google.json"))["project_id"],

# Read from BigQuery
dialect = BigqueryDialect(project=project, dataset='<dataset>', table='<table>')
resource = Resource(service, dialect=dialect)
pprint(resource.read_rows())
```

If you'd like to treat BigQuery dataset as a tabular storage:

```python title="Python"
from pprint import pprint
from frictionless import Package

package = Package.from_bigquery(service=service, project=project, dataset='<dataset>')
pprint(package)
for resource in package.resources:
  pprint(resource.read_rows())
```

## Writing Data

> **[NOTE]** Timezone information is ignored for `datetime` and `time` types.

We can export a package to a BigQuery dataset:

```python
from pprint import pprint
from frictionless import Package

package = Package('path/to/datapackage.json')
package.to_bigquery(service, project=project, dataset='<dataset>')
```

Also, it's possible to save a resource as a Bigquery table using `resource.write()`.

## Using Dialect

There is the `BigqueryDialect` to configure how Frictionles works with BigQuery:

```python
from pprint import pprint
from frictionless import Resource
from frictionless.plugins.bigquery import BigqueryDialect

dialect = BigqueryDialect(project=project, dataset='<dataset>', table='<table>'
resource = Resource(service, dialect=dialect)
pprint(resource.read_rows())
```

References:
- [BigQuery Dialect](../../references/formats-reference.md#bigquery)
