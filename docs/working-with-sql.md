# Working with SQL

> Status: **EXPERIMENTAL**

Frictionless supports reading and writing SQL databases.

```sh
! pip install frictionless[sql]
```

## Reading from SQL

You can read SQL database:

```py
from frictionless import Package

package = Package.from_pandas(url='postgresql://mydatabase')
print(package)
for resource in package.resources:
  print(resource.read_rows())
```

## Wriring to SQL

> **[NOTE]** Timezone information is ignored for `datetime` and `time` types.

You can write SQL databases:

```py
from frictionless import Package

package = Package('path/to/datapackage.json')
package.to_spss(utl='postgresql://mydatabase')
```

## Configuring SQL

There is a dialect to configure how Frictionless read and write files in this format. For example:

```py
from frictionless import Resource
from frictionless.plugins.sql import SqlDialect

dialect = SqlDialect(table='table', order_by='field')
resource = Resource('postgresql://database', dialect=dialect)
```

References:
- [SQL Dialect](https://frictionlessdata.io/tooling/python/dialects-reference/#sql)
