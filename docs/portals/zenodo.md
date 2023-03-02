# Zenodo Portal

Zenodo API makes data sharing between frictionless framework and Zenodo easy. The data from the Zenodo repo can be read from
as well as written to zenodo seamlessly. The api uses 'zenodopy' library underneath to communicate with Zenodo REST API.

## Installation

We need to install zenodo extra dependencies to use this feature:

```bash tabs=CLI
pip install frictionless[zenodo] --pre
pip install 'frictionless[zenodo]' --pre # for zsh shell
```

## Reading Package

You can read data from a zenodo repository as follows:

```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

package = Package("https://zenodo.org/record/7078768")
package.infer()
print(package)
```
```
{'title': 'Frictionless Data Test Dataset Without Descriptor',
 'resources': [{'name': 'capitals',
                'type': 'table',
                'path': 'capitals.csv',
                'scheme': 'https',
                'format': 'csv',
                'encoding': 'utf-8',
                'mediatype': 'text/csv',
                'dialect': {'csv': {'skipInitialSpace': True}},
                'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                                      {'name': 'cid', 'type': 'integer'},
                                      {'name': 'name', 'type': 'string'}]}},
               {'name': 'table',
                'type': 'table',
                'path': 'table.xls',
                'scheme': 'https',
                'format': 'xls',
                'encoding': 'utf-8',
                'mediatype': 'application/vnd.ms-excel',
                'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                                      {'name': 'name', 'type': 'string'}]}}]}
```

To increase the access limit, pass 'apikey' as the param to the reader function as follows:

```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

control = portals.ZenodoControl(apikey=apikey)
package = Package("https://zenodo.org/record/7078768", control=control)
print(package)
```

The `reader` function can read package from repos with/without data package descriptor. If the repo does not have the descriptor it will create the descriptor with the name same as the repo name as shown in the example above. By default, the function reads files of type csv, xlsx, xls etc which is supported by frictionless framework but we can set the file types using control parameters also.

If the repo has a descriptor it simply returns the descriptor as shown below:

```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

package = Package("https://zenodo.org/record/7078760")
package.infer()
print(package)
```
```
{'name': 'testing',
 'title': 'Frictionless Data Test Dataset',
 'resources': [{'name': 'data',
                'path': 'data.csv',
                'schema': {'fields': [{'name': 'id',
                                       'type': 'string',
                                       'constraints': {'required': True}},
                                      {'name': 'name', 'type': 'string'},
                                      {'name': 'description', 'type': 'string'},
                                      {'name': 'amount', 'type': 'number'}],
                           'primaryKey': ['id']}},
               {'name': 'data2',
                'path': 'data2.csv',
                'schema': {'fields': [{'name': 'parent', 'type': 'string'},
                                      {'name': 'comment', 'type': 'string'}],
                           'foreignKeys': [{'fields': ['parent'],
                                            'reference': {'resource': 'data',
                                                          'fields': ['id']}}]}}]}
```
Once you read the package from the repo, you can then easily access the resources and its data, for example:

```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

package = Package("https://zenodo.org/record/7078760")
pprint(package.get_resource('data').read_rows())
```
```
[{'amount': Decimal('10000.5'),
  'description': 'Taxes we collect',
  'id': 'A3001',
  'name': 'Taxes'},
 {'amount': Decimal('2000.5'),
  'description': 'Parking fees we collect',
  'id': 'A5032',
  'name': 'Parking Fees'}]
```
You can apply any functions available in frictionless framework. Here is an example of applying validation to the
package that was read.

```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

package = Package("https://zenodo.org/record/7078760")
report = catalog.packages[0].validate()
pprint(report)
```
```
{'valid': True,
 'stats': {'tasks': 1, 'warnings': 0, 'errors': 0, 'seconds': 0.655},
 'warnings': [],
 'errors': [],
 'tasks': [{'valid': True,
            'name': 'first-http-resource',
            'type': 'table',
            'place': 'https://raw.githubusercontent.com/fdtester/test-repo-with-datapackage-yaml/master/data/capitals.csv',
            'labels': ['id', 'cid', 'name'],
            'stats': {'md5': '154d822b8c2aa259867067f01c0efee5',
                      'sha256': '5ec3d8a4d137891f2f19ab9d244cbc2c30a7493f895c6b8af2506d9b229ed6a8',
                      'bytes': 76,
                      'fields': 3,
                      'rows': 5,
                      'warnings': 0,
                      'errors': 0,
                      'seconds': 0.651},
            'warnings': [],
            'errors': []}]}

```

## Reading Catalog

Catalog is a container for the packages. We can read single/multiple repositories from Zenodo repo and create a catalog.

```python tabs=Python
from pprint import pprint
from frictionless import portals, Catalog

control = portals.ZenodoControl(search='notes:"TDWD"')
catalog = Catalog(control=control)
catalog.infer()
print("Total packages", len(catalog.packages))
print(catalog.packages)
```
```
Total packages 2
[{'title': 'Frictionless Data Test Dataset Without Descriptor',
 'resources': [{'name': 'countries',
                'type': 'table',
                'path': 'countries.csv',
                'scheme': 'https',
                'format': 'csv',
                'encoding': 'utf-8',
                'mediatype': 'text/csv',
                'dialect': {'headerRows': [2]},
                'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                                      {'name': 'neighbor_id', 'type': 'string'},
                                      {'name': 'name', 'type': 'string'},
                                      {'name': 'population',
                                       'type': 'string'}]}}]}, {'title': 'Frictionless Data Test Dataset Without Descriptor',
 'resources': [{'name': 'capitals',
                'type': 'table',
                'path': 'capitals.csv',
                'scheme': 'https',
                'format': 'csv',
                'encoding': 'utf-8',
                'mediatype': 'text/csv',
                'dialect': {'csv': {'skipInitialSpace': True}},
                'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                                      {'name': 'cid', 'type': 'integer'},
                                      {'name': 'name', 'type': 'string'}]}},
               {'name': 'table',
                'type': 'table',
                'path': 'table.xls',
                'scheme': 'https',
                'format': 'xls',
                'encoding': 'utf-8',
                'mediatype': 'application/vnd.ms-excel',
                'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                                      {'name': 'name', 'type': 'string'}]}}]}]
```

In the above example we are using search text to filter the repositories to reduce the result size to small number. However, the search field is not mandatory. We can simply use 'control' parameters and create the catalog from a single repo, for example:

```python tabs=Python
from pprint import pprint
from frictionless import portals, Catalog

control = portals.ZenodoControl(record="7078768")
catalog = Catalog(control=control)
catalog.infer()
print("Total packages", len(catalog.packages))
print(catalog.packages)
```
```
Total packages 1
[{'title': 'Frictionless Data Test Dataset Without Descriptor',
 'resources': [{'name': 'capitals',
                'type': 'table',
                'path': 'capitals.csv',
                'scheme': 'https',
                'format': 'csv',
                'encoding': 'utf-8',
                'mediatype': 'text/csv',
                'dialect': {'csv': {'skipInitialSpace': True}},
                'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                                      {'name': 'cid', 'type': 'integer'},
                                      {'name': 'name', 'type': 'string'}]}},
               {'name': 'table',
                'type': 'table',
                'path': 'table.xls',
                'scheme': 'https',
                'format': 'xls',
                'encoding': 'utf-8',
                'mediatype': 'application/vnd.ms-excel',
                'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                                      {'name': 'name', 'type': 'string'}]}}]}]
```
As shown in the first catalog example above, we can use different search queries to filter the repos. The above example searches for all the repos which has 'notes:"TDWD"' text in readme files. Similary we can use many different queries combining many terms, phrases or field
search. To get full list of different queries you can check the zenodo official document [here](https://help.zenodo.org/guides/search).

Some examples of the search queries are:

```
"open science"
title:"open science"
+description:"frictionless" +title:"Bionomia"
+publication_date:[2022-10-01 TO 2022-11-01] +title:"frictionless"
```
We can search for different terms such as "open science" and also use '+' to specify mandatory. If "+" is not specified, it will be optional and will apply 'OR' logic to the search. We can also use field search. All the search queries supported by Zenodo Rest API can be
used.

If we want to read the list of repositories which has term "+frictionlessdata +science" then we write search query as follows:
```python tabs=Python
from pprint import pprint
from frictionless import portals, Catalog

control = portals.ZenodoControl(search='+frictionlessdata +science')
catalog = Catalog(control=control)
print("Total Packages", len(catalog.packages))
```
```
Total Packages 1
```
There is only one repository having terms '+frictionlessdata +science', so it returned only one repository.

We can also read repositories in defined order using 'sort' param. Here we are trying to read the repos with 'creators.name:"FD Tester"' in recently updated order, for example:
```python script tabs=Python
from pprint import pprint
from frictionless import portals, Catalog

catalog = Catalog(
       control=portals.ZenodoControl(
           search='creators.name:"FD Tester"',
           sort="mostrecent",
           page=1,
           size=1,
       ),
   )
catalog.infer()
```
```
[{'name': 'test-repo-resources-with-http-data-csv',
 'title': 'Test Write File - Remote',
 'resources': [{'name': 'first-http-resource',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-with-datapackage-yaml/master/data/capitals.csv',
                'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                                      {'name': 'cid', 'type': 'string'},
                                      {'name': 'name', 'type': 'string'}]}}]}]
```

## Publishing Data

To write data to the repository, we use `Package.publish` function as follows:
```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

control = portals.ZenodoControl(
        metafn="data/zenodo/meta.json",
        apikey=apikey
    )
package = Package("484/package-to-write/datapackage.json")
deposition_id = package.publish(control=control)
print(deposition_id)
```
```
1123500
```
To publish the data, we need to provide metadata for the Zenodo repo which we are sending using "meta.json". In order to be able to publish/write to respository, we need to have the api token with 'repository write' access. If the package is successfully published, the deposition_id will be returned as shown in the example above.

For testing, we can pass sandbox url using base_url param

```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

control = portals.ZenodoControl(
        metafn="data/zenodo/meta.json",
        apikey=apikey_sandbox,
        base_url="https://sandbox.zenodo.org/api/"
    )
package = Package("484/package-to-write/datapackage.json")
deposition_id = package.publish(control=control)
```

If the metadata file is not provided, then the api will read available data from the package file. Metadata will be generated using title, contributors and description from Package descriptor.

```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

control = portals.ZenodoControl(
        apikey=apikey_sandbox,
        base_url="https://sandbox.zenodo.org/api/"
    )
package = Package("484/package-to-write/datapackage.json")
deposition_id = package.publish(control=control)
```

## Configuration

We can control the behavior of all the above three functions using various params.

For example, to read only 'csv' files in package we use the following code:

```python tabs=Python
from pprint import pprint
from frictionless import portals, Package

control = portals.ZenodoControl(formats=["csv"], record="7078725", apikey=apikey)
package = Package(control=control)
print(package)
```
```
{'name': 'test-repo-without-datapackage',
 'resources': [{'name': 'capitals',
                'type': 'table',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/capitals.csv',
                'scheme': 'https',
                'format': 'csv',
                'mediatype': 'text/csv'},
               {'name': 'countries',
                'type': 'table',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-without-datapackage/master/data/countries.csv',
                'scheme': 'https',
                'format': 'csv',
                'mediatype': 'text/csv'}]}
```

In order to read first page of the search result and create a catalog, we use `page` and `size` params as follows:

```python tabs=Python
from pprint import pprint
from frictionless import portals, Catalog

catalog = Catalog(
       control=portals.ZenodoControl(
           search='creators.name"FD Tester"',
           sort="mostrecent",
           page=1,
           size=1,
       ),
   )
print(catalog.packages)
```
```
[{'name': 'test-repo-resources-with-http-data-csv',
 'title': 'Test Write File - Remote',
 'resources': [{'name': 'first-http-resource',
                'path': 'https://raw.githubusercontent.com/fdtester/test-repo-with-datapackage-yaml/master/data/capitals.csv',
                'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                                      {'name': 'cid', 'type': 'string'},
                                      {'name': 'name', 'type': 'string'}]}}]}]
```
## Reference

```yaml reference
references:
  - frictionless.portals.ZenodoControl
```
```
