# Working with SPSS

> Status: **EXPERIMENTAL**

Frictionless supports reading and writing SPSS files.

```sh
! pip install frictionless[spss]
```


## Reading from SPSS

You can read SPSS files:

```py
from frictionless import Package

package = Package.from_pandas(basepath='<dir with your .SAV files>')
print(package)
for resource in package.resources:
  print(resource.read_rows())
```


## Wriring to SPSS

You can write SPSS files:

```py
from frictionless import Package

package = Package('path/to/datapackage.json')
package.to_spss(basepath='target')
```


## Configuring SPSS

> Not supported yet