# Sql Format

Frictionless supports reading and writing SQL databases.

```bash tabs=CLI
pip install frictionless[sql]
pip install 'frictionless[sql]' # for zsh shell
```

## Reading Data

You can read SQL database:

```python tabs=Python
from pprint import pprint
from frictionless import Package

package = Package.from_sql('postgresql://database')
pprint(package)
for resource in package.resources:
  pprint(resource.read_rows())
```

### SQLite

Here is a example of reading a table from a SQLite database using basepath:

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
