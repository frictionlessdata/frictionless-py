# Sql Format

Frictionless supports reading and writing SQL databases.

## Supported Databases

Frictionless Framework in-general support many databases that can be used with `sqlalchemy`. Here is a list of the databases with tested support:

### SQLite

> https://www.sqlite.org/index.html

It's a well-tested default database used by Frictionless:

```bash tabs=CLI
pip install frictionless[sql]
```

### PostgreSQL

> https://www.postgresql.org/

This database is well-tested and provides the most data types:

```bash tabs=CLI
pip install frictionless[postgresql]
```

### MySQL

> https://www.mysql.com/

Another popular databases having been tested with Frictionless:

```bash tabs=CLI
pip install frictionless[mysql]
```

### DuckDB

> https://duckdb.org/

DuckDB is a reletively new database and, currently, Frictionless support is experimental:

```bash tabs=CLI
pip install frictionless[duckdb]
```

## Reading Data

You can read SQL database:

```python tabs=Python
from frictionless import Resource, formats

control = SqlControl(table="test_table", basepath='data')
with Resource(path="sqlite:///sqlite.db", control=control) as resource:
    print(resource.read_rows())
```

## Writing Data

You can write SQL databases:

```python tabs=Python
from frictionless import Package

package = Package('path/to/datapackage.json')
package.publish('postgresql://database')
```

## Configuration

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python tabs=Python
from frictionless import Resource, formats

control = SqlControl(table='table', order_by='field', where='field > 20')
resource = Resource('postgresql://database', control=control)
```

## Reference

```yaml reference
references:
  - frictionless.formats.SqlControl
```
