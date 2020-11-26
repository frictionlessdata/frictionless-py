# Working with SQL

> Status: **STABLE**

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

You can write SQL databases:

```py
from frictionless import Package

package = Package('path/to/datapackage.json')
package.to_spss(utl='postgresql://mydatabase')
```


## Configuring SQL

> Not supported yet