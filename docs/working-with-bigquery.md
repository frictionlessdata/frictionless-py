# Working with BigQuery

> Status: **EXPERIMENTAL**

Frictionless supports both reading tables from BigQuery source and treating a BigQuery dataset as a tabular data storage.

```sh
! pip install frictionless[bigquery]
```

## Reading from BigQuery

You can read from this source using `Package/Resource` or `Table` API, for example:

```py
import os
import json
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
dialect = BigqueryDialect(project=project, dataset='<dataset>', table='<table>'
resource = Resource(path=service, dialect=dialect)
print(resource.read_rows())
```

If you'd like to treat BigQuery dataset as a tabular storage:

```py
package = Package.from_bigquery(service=service, project=project, dataset='<dataset>')
print(package)
for resource in package.resources:
  print(resource.read_rows())
```

## Writing to BigQuery

> **[NOTE]** Timezone information is ignored for `datetime` and `time` types.

We can export a package to a BigQuery dataset:

```py
package = Package('path/to/datapackage.json')
package.to_bigquery(service=service, project=project, dataset='<dataset>')
```

## Configuring BigQuery

There are two options to configure BigQuery interactions. First of all, there are different options for these functions:

```
Resource/Package.from_bigquery
resource/package.to_bigquery
```

Secondly, there a dialect:

```py
dialect = BigqueryDialect(project=project, dataset='<dataset>', table='<table>'
resource = Resource(path=service, dialect=dialect)
print(resource.read_rows())
```

References:
- [BigQuery Dialect](https://frictionlessdata.io/tooling/python/formats-reference/#bigquery)
