# Cell Steps

The Cell steps are responsible for cell operations like converting, replacing, or formating, along with others.

## Convert Cells

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_convert(value="n/a", field_name="name"),
    ]
)
print(target.schema)
print(target.to_view())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-------+------------+
| id | name  | population |
+====+=======+============+
|  1 | 'n/a' |         83 |
+----+-------+------------+
|  2 | 'n/a' |         66 |
+----+-------+------------+
|  3 | 'n/a' |         47 |
+----+-------+------------+
```

## Fill Cells

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_replace(pattern="france", replace=None),
        steps.cell_fill(field_name="name", value="FRANCE"),
    ]
)
print(target.schema)
print(target.to_view())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-----------+------------+
| id | name      | population |
+====+===========+============+
|  1 | 'germany' |         83 |
+----+-----------+------------+
|  2 | 'FRANCE'  |         66 |
+----+-----------+------------+
|  3 | 'spain'   |         47 |
+----+-----------+------------+
```

## Format Cells

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_format(template="Prefix: {0}", field_name="name"),
    ]
)
print(target.schema)
print(target.to_view())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-------------------+------------+
| id | name              | population |
+====+===================+============+
|  1 | 'Prefix: germany' |         83 |
+----+-------------------+------------+
|  2 | 'Prefix: france'  |         66 |
+----+-------------------+------------+
|  3 | 'Prefix: spain'   |         47 |
+----+-------------------+------------+
```

## Interpolate Cells

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_interpolate(template="Prefix: %s", field_name="name"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 1, 'name': 'Prefix: germany', 'population': 83},
 {'id': 2, 'name': 'Prefix: france', 'population': 66},
 {'id': 3, 'name': 'Prefix: spain', 'population': 47}]
```

## Merge Cells

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
     source,
     steps=[
     	 # seperator argument can be used to set delimeter. Default value is '-'
    	 # preserve argument keeps the original fields
         steps.field_merge(name="details", from_names=["name", "population"], preserve=True)
     ],
)
print(target.schema)
print(target.to_view())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'details', 'type': 'string'}]}
+----+-----------+------------+--------------+
| id | name      | population | details      |
+====+===========+============+==============+
|  1 | 'germany' |         83 | 'germany-83' |
+----+-----------+------------+--------------+
|  2 | 'france'  |         66 | 'france-66'  |
+----+-----------+------------+--------------+
|  3 | 'spain'   |         47 | 'spain-47'   |
+----+-----------+------------+--------------+
 ```


## Pack Cells

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
    	# field_type returns packed fields as JSON Object. Default value for field_type is 'array'
    	# preserve argument keeps the original fields
        steps.field_pack(name="details", from_names=["name", "population"], field_type="object", preserve=True)
    ]
)
print(target.schema)
print(target.to_view())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'details', 'type': 'object'}]}
+----+-----------+------------+-----------------------------------------+
| id | name      | population | details                                 |
+====+===========+============+=========================================+
|  1 | 'germany' |         83 | {'name': 'germany', 'population': '83'} |
+----+-----------+------------+-----------------------------------------+
|  2 | 'france'  |         66 | {'name': 'france', 'population': '66'}  |
+----+-----------+------------+-----------------------------------------+
|  3 | 'spain'   |         47 | {'name': 'spain', 'population': '47'}   |
+----+-----------+------------+-----------------------------------------+
```

## Replace Cells

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_replace(pattern="france", replace="FRANCE"),
    ]
)
print(target.schema)
print(target.to_view())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-------------------+------------+
| id | name              | population |
+====+===================+============+
|  1 | 'Prefix: germany' |         83 |
+----+-------------------+------------+
|  2 | 'Prefix: france'  |         66 |
+----+-------------------+------------+
|  3 | 'Prefix: spain'   |         47 |
+----+-------------------+------------+
```

## Set Cells

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
          steps.cell_set(field_name="population", value=100),
    ]
)
print(target.schema)
print(target.to_view())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-----------+------------+
| id | name      | population |
+====+===========+============+
|  1 | 'germany' |        100 |
+----+-----------+------------+
|  2 | 'france'  |        100 |
+----+-----------+------------+
|  3 | 'spain'   |        100 |
+----+-----------+------------+
```
