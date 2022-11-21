---
script:
  basepath: data
---

# Package Class

The Data Package is a core Frictionless Data concept meaning a set of resources with additional metadata provided. You can read [Data Package Standard](https://specs.frictionlessdata.io/data-package/) for more information.

## Creating Package

Let's create a data package:

```python tabs=Python
from frictionless import Package, Resource

package = Package('table.csv') # from a resource path
package = Package('tables/*') # from a resources glob
package = Package(['tables/chunk1.csv', 'tables/chunk2.csv']) # from a list
package = Package('package/datapackage.json') # from a descriptor path
package = Package({'resources': {'path': 'table.csv'}}) # from a descriptor
package = Package(resources=[Resource(path='table.csv')]) # from arguments
```

As you can see it's possible to create a package providing different kinds of sources which will be detected to have some type automatically (e.g. whether it's a glob or a path). It's possible to make this step more explicit:

```python tabs=Python
from frictionless import Package, Resource

package = Package(resources=[Resource(path='table.csv')]) # from arguments
package = Package('datapackage.json') # from a descriptor
```

## Describing Package

The standards support a great deal of package metadata which is possible to have with Frictionless Framework too:

```python script tabs=Python
from frictionless import Package, Resource

package = Package(
    name='package',
    title='My Package',
    description='My Package for the Guide',
    resources=[Resource(path='table.csv')],
    # it's possible to provide all the official properties like homepage, version, etc
)
print(package)
```

If you have created a package, for example, from a descriptor you can access this properties:

```python script tabs=Python
from frictionless import Package

package = Package('datapackage.json')
print(package.name)
# and others
```

And edit them:

```python script tabs=Python
from frictionless import Package

package = Package('datapackage.json')
package.name = 'new-name'
package.title = 'New Title'
package.description = 'New Description'
# and others
print(package)
```

## Resource Management

The core purpose of having a package is to provide an ability to have a set of resources. The Package class provides useful methods to manage resources:

```python script tabs=Python
from frictionless import Package, Resource

package = Package('datapackage.json')
print(package.resources)
print(package.resource_names)
package.add_resource(Resource(name='new', data=[['key1', 'key2'], ['val1', 'val2']]))
resource = package.get_resource('new')
print(package.has_resource('new'))
package.remove_resource('new')
```

## Saving Descriptor

As any of the Metadata classes the Package class can be saved as JSON or YAML:

```python tabs=Python
from frictionless import Package
package = Package('tables/*')
package.to_json('datapackage.json') # Save as JSON
package.to_yaml('datapackage.yaml') # Save as YAML
```

## Reference

```yaml reference
references:
  - frictionless.Package
```
