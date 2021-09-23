---
title: CKAN Tutorial
sidebar_label: CKAN
---

> This functionality requires an experimental `ckan` plugin. [Read More](../../references/plugins-reference.md)

Frictionless supports reading and writing CKAN datasets.

```bash title="CLI"
pip install frictionless[ckan]
```

## Reading Data

You can read a CKAN dataset:

```python
from pprint import pprint
from frictionless import Package

package = Package.from_ckan('<base_url>', dataset_id='<dataset_id>', api_key='<api_key>')
pprint(package)
for resource in package.resources:
  pprint(resource.read_rows())
```

## Writing Data

> **[NOTE]** Timezone information is ignored for `datetime` and `time` types.

You can write a dataset to CKAN:

```python
from frictionless import Package

package = Package('path/to/datapackage.json')
package.to_ckan('<base_url>', dataset_id='<dataset_id>', api_key='<api_key>')
```

## Configuring Data

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python
from frictionless import Resource
from frictionless.plugins.ckan import CkanDialect

dialect = CkanDialect(resource='resource', dataset='dataset', apikey='apikey')
resource = Resource('https://ckan-portal.com', format='ckan', dialect=dialect)
```

For more control on the CKAN query you can use `fields`, `limit`, `sort` and `filter` in the dialect. For example:

```python
from frictionless import Resource
from frictionless.plugins.ckan import CkanDialect

dialect = CkanDialect(
  resource='resource',
  dataset='dataset',
  apikey='apikey',
  fields=['date','key','value'],
  limit=10,
  sort='date desc',
  filter={'key': 'value'}
)
resource = Resource('https://ckan-portal.com', format='ckan', dialect=dialect)
```

References:
- [Ckan Dialect](../../references/formats-reference.md#ckan)
