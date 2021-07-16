---
title: SQL Tutorial
sidebar_label: SQL
---

> This functionality requires an experimental `sql` plugin. [Read More](../../references/plugins-reference.md)

Frictionless supports reading and writing SQL databases.

```bash title="CLI"
pip install frictionless[sql]
```

## Reading Data

You can read SQL database:

```python title="Python"
from pprint import pprint
from frictionless import Package

package = Package.from_sql('postgresql://database')
pprint(package)
for resource in package.resources:
  pprint(resource.read_rows())
```

## Writing Data

> **[NOTE]** Timezone information is ignored for `datetime` and `time` types.

You can write SQL databases:

```python
from frictionless import Package

package = Package('path/to/datapackage.json')
package.to_sql('postgresql://database')
```

## Configuring Data

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python
from frictionless import Resource
from frictionless.plugins.sql import SqlDialect

dialect = SqlDialect(table='table', order_by='field', where='field > 20')
resource = Resource('postgresql://database', dialect=dialect)
```

References:
- [SQL Dialect](../../references/formats-reference.md#sql)
