# Resource Steps

The Resource steps are only available for a package transformation. This includes some basic resource management operations like adding or removing resources along with the hierarchical `transform_resource` step.

## Add Resource

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_add(name='extra', path='transform.csv'),
    ],
)
print(target.resource_names)
print(target.get_resource('extra').schema)
print(target.get_resource('extra').to_view())
```
```
['main', 'extra']
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-----------+------------+
| id | name      | population |
+====+===========+============+
|  1 | 'germany' |         83 |
+----+-----------+------------+
|  2 | 'france'  |         66 |
+----+-----------+------------+
|  3 | 'spain'   |         47 |
+----+-----------+------------+
```

## Remove Resource

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_remove(name='main'),
    ],
)
pprint(target)
```
```
{'profile': 'data-package', 'resources': []}
```

## Transform Resource

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_add(name='extra', path='transform.csv'),
        steps.resource_transform(name='main', steps=[
            steps.table_merge(resource='extra'),
            steps.row_sort(field_names=['id'])
        ]),
        steps.resource_remove(name="extra"),
    ],
)
print(target.resource_names)
print(target.get_resource('main').schema)
print(target.get_resource('main').to_view())
```
```
['main']
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-----------+------------+
| id | name      | population |
+====+===========+============+
|  1 | 'germany' |         83 |
+----+-----------+------------+
|  1 | 'germany' |         83 |
+----+-----------+------------+
|  2 | 'france'  |         66 |
+----+-----------+------------+
|  2 | 'france'  |         66 |
+----+-----------+------------+
|  3 | 'spain'   |         47 |
+----+-----------+------------+
```

## Update Resource

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_update(name='main', title='Main Resource', description='For the docs'),
    ],
)
pprint(target.get_resource('main'))
```
```
{'description': 'For the docs',
 'encoding': 'utf-8',
 'format': 'csv',
 'hashing': 'md5',
 'name': 'main',
 'path': 'transform.csv',
 'profile': 'tabular-data-resource',
 'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                       {'name': 'name', 'type': 'string'},
                       {'name': 'population', 'type': 'integer'}]},
 'scheme': 'file',
 'title': 'Main Resource'}
```
