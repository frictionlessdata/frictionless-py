---
title: Package Guide
cleanup:
  - rm package.json
  - rm package.yaml
---

The Data Package is a core Frictionless Data concept meaning a set of resources with additional metadata provided. You can read [Data Package Spec](https://specs.frictionlessdata.io/data-package/) for more information.

## Creating Package

Let's create a data package:

```python script title="Python"
from frictionless import Package, Resource

package = Package('data/table.csv') # from a resource path
package = Package('data/tables/*') # from a resources glob
package = Package(['data/tables/chunk1.csv', 'data/tables/chunk2.csv']) # from a list
package = Package('data/package/datapackage.json') # from a descriptor path
package = Package({'resources': {'path': 'data/table.csv'}}) # from a descriptor
package = Package(resources=[Resource(path='data/table.csv')]) # from arguments
```

As you can see it's possible to create a package providing different kinds of sources which will be detected to have some type automatically (e.g. whether it's a glob or a path). It's possible to make this step more explicit:

```python title="Python"
from frictionless import Package, Resource

package = Package(resources=[Resource(path='data/table.csv')]) # from resources
package = Package(descriptor='data/package/datapackage.json') # from a descriptor
```

## Describing Package

The specs support a great deal of package metadata which is possible to have with Frictionless Framework too:

```python script title="Python"
from frictionless import Package, Resource

package = Package(
    name='package',
    title='My Package',
    description='My Package for the Guide',
    resources=[Resource(path='data/table.csv')],
    # it's possible to provide all the official properties like homepage, version, etc
)
```

If you have created a package, for example, from a descriptor you can access this properties:

```python script title="Python"
from frictionless import Package

package = Package('data/package/datapackage.json')
package.name
package.title
package.description
# and others
```

And edit them:

```python script title="Python"
from frictionless import Package

package = Package('data/package/datapackage.json')
package.name = 'new-name'
package.title = 'New Title'
package.description = 'New Description'
# and others
```

## Resource Management

The core purpose of having a package is to provide an ability to have a set of resources. The Package class provides useful methods to manage resources:

```python script title="Python"
from frictionless import Package, Resource

package = Package('data/package/datapackage.json')
print(package.resources)
print(package.resource_names)
package.add_resource(Resource(name='new', data=[['key1', 'key2'], ['val1', 'val2']]))
resource = package.get_resource('new')
print(package.has_resource('new'))
package.remove_resource('new')
```
```
[{'name': 'data', 'path': 'data.csv', 'schema': {'fields': [{'name': 'id', 'type': 'string', 'constraints': {'required': True}}, {'name': 'name', 'type': 'string'}, {'name': 'description', 'type': 'string'}, {'name': 'amount', 'type': 'number'}], 'primaryKey': 'id'}}, {'name': 'data2', 'path': 'data2.csv', 'schema': {'fields': [{'type': 'string', 'name': 'parent'}, {'type': 'string', 'name': 'comment'}], 'foreignKeys': [{'fields': 'parent', 'reference': {'resource': 'data', 'fields': 'id'}}]}}]
['data', 'data2']
True
```

## Saving Descriptor

As any of the Metadata classes the Package class can be saved as JSON or YAML:

```python script title="Python"
from frictionless import Package
package = Package('data/tables/*')
package.to_json('package.json') # Save as JSON
package.to_yaml('package.yaml') # Save as YAML
```

## Package Options

The Package constructor accept a few additional options to tweak how it and the underlaying resources will work:

### Basepath

Will make all the paths treated as relative to this path.

### Detector

[Detector](detector-guide.md) object to tweak metadata detection.

### Onerror

There are 3 possible values for reacting on tabular errors:
- ignore (default)
- warn
- raise

### Trusted

By default an error will be raised on [unsafe paths](https://specs.frictionlessdata.io/data-resource/#url-or-path). Setting `trusted` to `True` will disable this behaviour.

### Hashing

Will be passed to underlaying resources as a default hashing algorithm.

[Detector](detector-guide.md) object to tweak metadata detection.

## Import/Export

It's possible to import and export package from/to:
- bigquery
- ckan
- sql
- zip

### BigQuery

> This functionality is in the draft state.

### Ckan

> This functionality is in the draft state.

### Sql

> This functionality is in the draft state.

### Zip

> This functionality is in the draft state.
