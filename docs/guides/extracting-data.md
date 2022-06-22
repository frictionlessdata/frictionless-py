---
title: Extracting Data
prepare:
  - cp data/country-3.csv country-3.csv
  - cp data/capital-3.csv capital-3.csv
cleanup:
  - rm country-3.csv
  - rm capital-3.csv
  - rm country.package.json
  - rm capital.resource.yaml
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

> This guide assumes basic familiarity with the Frictionless Framework. To learn more, please read the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction) and [Quick Start](https://framework.frictionlessdata.io/docs/guides/quick-start).

Extracting data means reading tabular data from a source. We can use various customizations for this process such as providing a file format, table schema, limiting fields or rows amount, and much more. This guide will discuss the main `extract` functions (`extract`, `extract_resource`, `extract_package`) and will then go into more advanced details about the `Resource Class`, `Package Class`, `Header Class`, and `Row Class`.

Let's see this with some real files:

> Download [`country-3.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/country-3.csv) to reproduce the examples (right-click and "Save link as").

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
cat country-3.csv
```
```csv title="Data: country-3.csv"
id,capital_id,name,population
1,1,Britain,67
2,3,France,67
3,2,Germany,83
4,5,Italy,60
5,4,Spain,47
```

</TabItem>
<TabItem value="python">

```python script
with open('country-3.csv') as file:
    print(file.read())
```
```csv title="Data: country-3.csv"
id,capital_id,name,population
1,1,Britain,67
2,3,France,67
3,2,Germany,83
4,5,Italy,60
5,4,Spain,47
```

</TabItem>
</Tabs>

> Download [`capital-3.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/capital-3.csv) to reproduce the examples (right-click and "Save link as").

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
cat capital-3.csv
```
```csv title="Data: capital-3.csv"
id,name
1,London
2,Berlin
3,Paris
4,Madrid
5,Rome
```

</TabItem>
<TabItem value="python">

```python script
with open('capital-3.csv') as file:
    print(file.read())
```
```csv title="Data: capital-3.csv"
id,name
1,London
2,Berlin
3,Paris
4,Madrid
5,Rome
```

</TabItem>
</Tabs>

To start, we will extract data from a resource:

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
frictionless extract country-3.csv
```
```csv title="Data: capital-3.csv"
# ----
# data: country-3.csv
# ----

==  ==========  =======  ==========
id  capital_id  name     population
==  ==========  =======  ==========
 1           1  Britain          67
 2           3  France           67
 3           2  Germany          83
 4           5  Italy            60
 5           4  Spain            47
==  ==========  =======  ==========
```

</TabItem>
<TabItem value="python">

```python script
from frictionless import extract
from tabulate import tabulate

rows = extract('country-3.csv')
print(tabulate(resource, headers="keys", tablefmt="rst"))
```
```csv title="Data: capital-3.csv"
====  ============  =======  ============
  id    capital_id  name       population
====  ============  =======  ============
   1             1  Britain            67
   2             3  France             67
   3             2  Germany            83
   4             5  Italy              60
   5             4  Spain              47
====  ============  =======  ============
```

</TabItem>
</Tabs>

## Extract Functions

The high-level interface for extracting data provided by Frictionless is a set of `extract` functions:
- `extract`: detects the source file type and extracts data accordingly
- `extract_resource`: accepts a resource descriptor and returns a data table
- `extract_package`: accepts a package descriptor and returns a map of the package's tables

As described in more detail in the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction), a resource is a single file, such as a data file, and a package is a set of files, such as a data file and a schema.

The command/function would be used as follows:

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash
frictionless extract your-table.csv
frictionless extract your-resource.json --type resource
frictionless extract your-package.json --type package
```

</TabItem>
<TabItem value="python">

```python script
from frictionless import extract

rows = extract('capital-3.csv')
resource = extract('capital-3.csv', type="resource")
package = extract('capital-3.csv', type="package")
```

</TabItem>
</Tabs>

The `extract` functions always reads data in the form of rows, into memory. The lower-level interfaces will allow you to stream data, which you can read about in the [Resource Class](#resource-class) section below.

## Extracting a Resource

A resource contains only one file. To extract a resource, we have three options. First, we can use the same approach as above, extracting from the data file itself:

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash
frictionless extract capital-3.csv
```
```csv title="Data: capital-3.csv"
# ----
# data: capital-3.csv
# ----

==  ======
id  name  
==  ======
 1  London
 2  Berlin
 3  Paris 
 4  Madrid
 5  Rome  
==  ======
```

</TabItem>
<TabItem value="python">

```python script title="Python"
from frictionless import extract
from tabulate import tabulate

resource = extract('capital-3.csv')
print(tabulate(resource, headers="keys", tablefmt="rst"))
```
```csv title="Data: capital-3.csv"
====  ======
  id  name
====  ======
   1  London
   2  Berlin
      Paris
   4  Madrid
   5  Rome
====  ======
```

</TabItem>
</Tabs>

Our second option is to extract the resource from a descriptor file by using the `extract_resource` function. A descriptor file is useful because it can contain different metadata and be stored on the disc.

As an example of how to use `extract_resource`, let's first create a descriptor file (note: this example uses YAML for the descriptor, but Frictionless also supports JSON):

```python script title="Python"
from frictionless import Resource

resource = Resource('capital-3.csv')
resource.infer()
# as an example, in the next line we will append the schema
resource.schema.missing_values.append('3') # will interpret 3 as a missing value
resource.to_yaml('capital.resource.yaml') # use resource.to_json for JSON format
```
You can also use a pre-made descriptor file.

Now, this descriptor file can be used to extract the resource:


<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
frictionless extract capital.resource.yaml
```
```csv title="Data: capital.resource.yaml"
# ----
# data: capital.resource.yaml
# ----

==  ======
id  name
==  ======
 1  London
 2  Berlin
    Paris
 4  Madrid
 5  Rome
==  ======
```

</TabItem>
<TabItem value="python">

```python title="Python"
from frictionless import extract
from tabulate import tabulate

data = extract('capital.resource.yaml')
print(tabulate(data, headers="keys", tablefmt="rst"))
```
```csv title="Data: capital.resource.yaml"
====  ======
  id  name
====  ======
   1  London
   2  Berlin
      Paris
   4  Madrid
   5  Rome
====  ======
```

</TabItem>
</Tabs>

So what has happened in this example? We set the textual representation of the number "3" to be a missing value. In the output we can see how the `id` number 3 now appears as `None` representing a missing value. This toy example demonstrates how the metadata in a descriptor can be used; other values like "NA" are more common for missing values.

You can read more advanced details about the [Resource Class below](#resource-class).

## Extracting a Package

The third way we can extract information is from a package, which is a set of two or more files, for instance, two data files and a corresponding metadata file.

As a primary example, we provide two data files to the `extract` command which will be enough to detect that it's a dataset. Let's start by using the command-line interface:

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
frictionless extract *-3.csv
```
```csv title="Data: *-3.csv"
# ----
# data: capital-3.csv
# ----

==  ======
id  name
==  ======
 1  London
 2  Berlin
 3  Paris
 4  Madrid
 5  Rome
==  ======


# ----
# data: country-3.csv
# ----

==  ==========  =======  ==========
id  capital_id  name     population
==  ==========  =======  ==========
 1           1  Britain          67
 2           3  France           67
 3           2  Germany          83
 4           5  Italy            60
 5           4  Spain            47
==  ==========  =======  ==========
```

</TabItem>
<TabItem value="python">

```python title="Python"
from frictionless import extract
from tabulate import tabulate

data = extract('*-3.csv')
for path, rows in data.items():
    print("#----")
    print("# data:", path)
    print("#----")
    print(tabulate(rows, headers="keys", tablefmt="rst"))
    print("\n")
```
```csv title="Data: *-3.csv"
#----
# data: capital-3.csv
#----
====  ======
  id  name
====  ======
   1  London
   2  Berlin
   3  Paris
   4  Madrid
   5  Rome
====  ======


#----
# data: country-3.csv
#----
====  ============  =======  ============
  id    capital_id  name       population
====  ============  =======  ============
   1             1  Britain            67
   2             3  France             67
   3             2  Germany            83
   4             5  Italy              60
   5             4  Spain              47
====  ============  =======  ============
```

</TabItem>
</Tabs>

We can also extract the package from a descriptor file using the `extract_package` function (Note: see the [Package Class section](#package-class) for the creation of the `country.package.yaml` file):

```python title="Python"
from frictionless import Package

package = Package('country.package.yaml')
pprint(package)
```

You can read more advanced details about the [Package Class below](#package-class).

> The following sections contain further, advanced details about the `Resource Class`, `Package Class`, `Header Class`, and `Row Class`.

## Resource Class

The Resource class provides metadata about a resource with read and stream functions. The `extract` functions always read rows into memory; Resource can do the same but it also gives a choice regarding output data which can be `rows`, `data`, `text`, or `bytes`. Let's try reading all of them.

### Reading Bytes

It's a byte representation of the contents:

```python script title="Python"
from frictionless import Resource

resource = Resource('country-3.csv')
pprint(resource.read_bytes())
```
```text title="Data: country-3.csv"
(b'id,capital_id,name,population\n1,1,Britain,67\n2,3,France,67\n3,2,Germany,8'
 b'3\n4,5,Italy,60\n5,4,Spain,47\n')
```

### Reading Text

It's a textual representation of the contents:

```python script title="Python"
from frictionless import Resource

resource = Resource('country-3.csv')
pprint(resource.read_text())
```
```text title="Data: country-3.csv"
('id,capital_id,name,population\n'
 '1,1,Britain,67\n'
 '2,3,France,67\n'
 '3,2,Germany,83\n'
 '4,5,Italy,60\n'
 '5,4,Spain,47\n')
```

### Reading Lists

For a tabular data there are raw representaion of the tabular contents:

```python script title="Python"
from frictionless import Resource

resource = Resource('country-3.csv')
pprint(resource.read_lists())
```
```text title="Data: country-3.csv"
[['id', 'capital_id', 'name', 'population'],
 ['1', '1', 'Britain', '67'],
 ['2', '3', 'France', '67'],
 ['3', '2', 'Germany', '83'],
 ['4', '5', 'Italy', '60'],
 ['5', '4', 'Spain', '47']]
```

### Reading Rows

For a tabular data there are row available which is are normalized lists presented as dictionaries:

```python script title="Python"
from frictionless import Resource

resource = Resource('country-3.csv')
pprint(resource.read_rows())
```
```text title="Data: country-3.csv"
[{'id': 1, 'capital_id': 1, 'name': 'Britain', 'population': 67},
 {'id': 2, 'capital_id': 3, 'name': 'France', 'population': 67},
 {'id': 3, 'capital_id': 2, 'name': 'Germany', 'population': 83},
 {'id': 4, 'capital_id': 5, 'name': 'Italy', 'population': 60},
 {'id': 5, 'capital_id': 4, 'name': 'Spain', 'population': 47}]
```

### Reading a Header

For a tabular data there is the Header object available:

```python script title="Python"
from frictionless import Resource

with Resource('country-3.csv') as resource:
    pprint(resource.header)
```
```text title="Data header: country-3.csv"
['id', 'capital_id', 'name', 'population']
```

### Streaming Interfaces

It's really handy to read all your data into memory but it's not always possible if a file is very big. For such cases, Frictionless provides streaming functions:

```python script title="Python"
from frictionless import Resource

with Resource('country-3.csv') as resource:
    resource.byte_stream
    resource.text_stream
    resource.list_stream
    resource.row_stream
```

## Package Class

The Package class provides functions to read the contents of a package. First of all, let's create a package descriptor:

```bash script title="CLI"
frictionless describe *-3.csv --json > country.package.json
```
Note that --json is used here to output the descriptor in JSON format. Without this, the default output is in YAML format as we saw above.

We can create a package from data files (using their paths) and then read the package's resources:

```python script title="Python"
from frictionless import Package

package = Package('*-3.csv')
pprint(package.get_resource('country-3').read_rows())
pprint(package.get_resource('capital-3').read_rows())
```
```text title="Data: country-3.csv, capital-3.csv"
[{'id': 1, 'capital_id': 1, 'name': 'Britain', 'population': 67},
 {'id': 2, 'capital_id': 3, 'name': 'France', 'population': 67},
 {'id': 3, 'capital_id': 2, 'name': 'Germany', 'population': 83},
 {'id': 4, 'capital_id': 5, 'name': 'Italy', 'population': 60},
 {'id': 5, 'capital_id': 4, 'name': 'Spain', 'population': 47}]
[{'id': 1, 'name': 'London'},
 {'id': 2, 'name': 'Berlin'},
 {'id': 3, 'name': 'Paris'},
 {'id': 4, 'name': 'Madrid'},
 {'id': 5, 'name': 'Rome'}]
```

The package by itself doesn't provide any read functions directly because it's just a contrainer. You can select a pacakge's resource and use the Resource API from above for data reading.

## Header Class

After opening a resource you get access to a `resource.header` object which describes the resource in more detail. This is a list of normalized labels but also provides some additional functionality. Let's take a look:

```python script title="Python"
from frictionless import Resource

with Resource('capital-3.csv') as resource:
  print(f'Header: {resource.header}')
  print(f'Labels: {resource.header.labels}')
  print(f'Fields: {resource.header.fields}')
  print(f'Field Names: {resource.header.field_names}')
  print(f'Field Positions: {resource.header.field_positions}')
  print(f'Errors: {resource.header.errors}')
  print(f'Valid: {resource.header.valid}')
  print(f'As List: {resource.header.to_list()}')
```
```
Header: ['id', 'name']
Labels: ['id', 'name']
Fields: [{'name': 'id', 'type': 'integer'}, {'name': 'name', 'type': 'string'}]
Field Names: ['id', 'name']
Field Positions: [1, 2]
Errors: []
Valid: True
As List: ['id', 'name']
```

The example above shows a case when a header is valid. For a header that contains errors in its tabular structure, this information can be very useful, revealing discrepancies, duplicates or missing cell information:

```python script title="Python"
from pprint import pprint
from frictionless import Resource

with Resource([['name', 'name'], ['value', 'value']]) as resource:
    pprint(resource.header.errors)
```
```
[{'code': 'duplicate-label',
  'description': 'Two columns in the header row have the same value. Column '
                 'names should be unique.',
  'fieldName': 'name2',
  'fieldNumber': 2,
  'fieldPosition': 2,
  'label': 'name',
  'labels': ['name', 'name'],
  'message': 'Label "name" in the header at position "2" is duplicated to a '
             'label: at position "1"',
  'name': 'Duplicate Label',
  'note': 'at position "1"',
  'rowPositions': [1],
  'tags': ['#table', '#header', '#label']}]
```

Please read the [API Reference](../references/api-reference#header) for more details.

## Row Class

The `extract`, `resource.read_rows()` and other functions return or yield row objects. In Python, this returns a dictionary with the following information. Note: this example uses the [Detector object](/docs/guides/framework/detector-guide), which tweaks how different aspects of metadata are detected.

```python script title="Python"
from frictionless import Resource, Detector

detector = Detector(schema_patch={'missingValues': ['1']})
with Resource('data/capital-3.csv', detector=detector) as resource:
  for row in resource:
    print(f'Row: {row}')
    print(f'Cells: {row.cells}')
    print(f'Fields: {row.fields}')
    print(f'Field Names: {row.field_names}')
    print(f'Field Positions: {row.field_positions}')
    print(f'Value of field "name": {row["name"]}') # accessed as a dict
    print(f'Row Position: {row.row_position}') # physical line number starting from 1
    print(f'Row Number: {row.row_number}') # counted row number starting from 1
    print(f'Blank Cells: {row.blank_cells}')
    print(f'Error Cells: {row.error_cells}')
    print(f'Errors: {row.errors}')
    print(f'Valid: {row.valid}')
    print(f'As Dict: {row.to_dict(json=False)}')
    print(f'As List: {row.to_list(json=True)}') # JSON compatible data types
    break
```
```
Row: {'id': None, 'name': 'London'}
Cells: ['1', 'London']
Fields: [{'name': 'id', 'type': 'integer'}, {'name': 'name', 'type': 'string'}]
Field Names: ['id', 'name']
Field Positions: [1, 2]
Value of field "name": London
Row Position: 2
Row Number: 1
Blank Cells: {'id': '1'}
Error Cells: {}
Errors: []
Valid: True
As Dict: {'id': None, 'name': 'London'}
As List: [None, 'London']
```

As we can see, this output provides a lot of information which is especially useful when a row is not valid. Our row is valid but we demonstrated how it can preserve data about missing values. It also preserves data about all cells that contain errors:

```python script title="Python"
from pprint import pprint
from frictionless import Resource

with Resource([['name'], ['value', 'value']]) as resource:
    for row in resource.row_stream:
        pprint(row.errors)
```
```
[{'cell': 'value',
  'cells': ['value', 'value'],
  'code': 'extra-cell',
  'description': 'This row has more values compared to the header row (the '
                 'first row in the data source). A key concept is that all the '
                 'rows in tabular data must have the same number of columns.',
  'fieldName': '',
  'fieldNumber': 1,
  'fieldPosition': 2,
  'message': 'Row at position "2" has an extra value in field at position "2"',
  'name': 'Extra Cell',
  'note': '',
  'rowNumber': 1,
  'rowPosition': 2,
  'tags': ['#table', '#row', '#cell']}]
```

Please read the [API Reference](../references/api-reference#row) for more details.
