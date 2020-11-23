# Working with SQL

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1hymBs2qCIXC-EzorBWVnBcXRzIay3Nk9)



> Status: **PLUGIN / STABLE**

Frictionless supports reading and writing SQL databases.


```bash
! pip install frictionless[sql]
```

## Reading from SQL

You can read SQL database:

```python
from frictionless import Package

package = Package.from_pandas(url='postgresql://mydatabase')
print(package)
for resource in package.resources:
  print(resource.read_rows())
```

## Wriring to SQL

You can write SQL databases:

```python
from frictionless import Package

package = Package('path/to/datapackage.json')
package.to_spss(utl='postgresql://mydatabase')
```

## Configuring SQL

> Not supported yet