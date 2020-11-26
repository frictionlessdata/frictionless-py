# Working with CKAN

>Status: **EXPERIMENTAL**

Frictionless supports reading and writing CKAN datasets.

```sh
! pip install frictionless[ckan]
```


## Reading from CKAN

You can read a CKAN dataset:

```py
from frictionless import Package

package = Package.from_ckan(base_url='<base_url>', dataset_id='<dataset_id>', api_key='<api_key>')
print(package)
for resource in package.resources:
  print(resource.read_rows())
```


## Wriring to CKAN

You can write a dataset to CKAN:

```py
from frictionless import Package

package = Package('path/to/datapackage.json')
package.to_ckan(base_url='<base_url>', dataset_id='<dataset_id>', api_key='<api_key>')
```


## Configuring CKAN

> CKAN dialect is not yet available