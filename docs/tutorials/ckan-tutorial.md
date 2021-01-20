---
title: CKAN Tutorial
sidebar_label: CKAN
---

:::caution Plugin
Status: **EXPERIMENTAL**
:::

Frictionless supports reading and writing CKAN datasets.

```bash
! pip install frictionless[ckan]
```


## Reading from CKAN

You can read a CKAN dataset:

```python
from frictionless import Package

package = Package.from_ckan(base_url='<base_url>', dataset_id='<dataset_id>', api_key='<api_key>')
print(package)
for resource in package.resources:
  print(resource.read_rows())
```


## Writing to CKAN

> **[NOTE]** Timezone information is ignored for `datetime` and `time` types.

You can write a dataset to CKAN:

```python
from frictionless import Package

package = Package('path/to/datapackage.json')
package.to_ckan(base_url='<base_url>', dataset_id='<dataset_id>', api_key='<api_key>')
```


## Configuring CKAN

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python
from frictionless import Resource
from frictionless.plugins.ckan import CkanDialect

dialect = CkanDialect(resource='resource', dataset='dataset', apikey='apikey')
resource = Resource('https://ckan-portal.com', format='ckan', dialect=dialect)
```


References:
- [CKAN Dialect](https://frictionlessdata.io/tooling/python/dialects-reference/#ckan)
