---
script:
  basepath: data
---

# Resource Steps

The Resource steps are only available for a package transformation. This includes some basic resource management operations like adding or removing resources along with the hierarchical `transform_resource` step.

## Add Resource

This step add a new resource to a data package.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_add(name='extra', descriptor={'path': 'transform.csv'}),
    ],
)
print(target.resource_names)
print(target.get_resource('extra').schema)
print(target.get_resource('extra').to_view())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=resource_add
name: frictionless.steps.resource_add
level: 4
```

## Remove Resource

This step remove an existent resource from a data package.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_remove(name='main'),
    ],
)
print(target)
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=resource_remove
name: frictionless.steps.resource_remove
level: 4
```

## Transform Resource

It's a hierarchical step allowing to transform a data package's resource. It's possible to use any resource steps as a part of this package step.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_transform(name='main', steps=[
            steps.row_sort(field_names=['name'])
        ]),
    ],
)
print(target.resource_names)
print(target.get_resource('main').schema)
print(target.get_resource('main').to_view())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=resource_transform
name: frictionless.steps.resource_transform
level: 4
```

## Update Resource

This step update a resource's metadata.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_update(
          name='main',
          descriptor={'title': 'Main Resource', 'description': 'For the docs'}
        ),
    ],
)
print(target.get_resource('main'))
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=resource_update
name: frictionless.steps.resource_update
level: 4
```
