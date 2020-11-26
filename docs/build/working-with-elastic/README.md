# Working with ElasticSearch

> Status: **EXPERIMENTAL**

Frictionless supports reading and writing ElasticSearch datasets.

```sh
! pip install frictionless[elastic]
```


## Reading from ElasticSearch

You can read a ElasticSearch dataset:

```py
from frictionless import Package

package = Package.from_elasticsearch(es='<es_instance>')
print(package)
for resource in package.resources:
  print(resource.read_rows())
```


## Wriring to ElasticSearch

You can write a dataset to ElasticSearch:

```py
from frictionless import Package

package = Package('path/to/datapackage.json')
package.to_ckan(es='<es_instance>')
```


## Configuring ElasticSearch

> ElasticSearch dialect is not yet available