---
prepare:
  commands:
    - cp data/countries.csv countries.csv
cleanup:
  commands:
      - rm countries.csv
      - rm countries.resource.yaml
---

# Basic Examples

> This example assumes that you are familiar with the concepts behind the Frictionless Framework. For an introduction, please read the [Introduction](introduction.md).

Let's start with an example dataset. We will look at a few raw data files that have recently been collected by an anthropologist. The anthropologist wants to publish this data in an open repository so her colleagues can also use this data. Before publishing the data, she wants to add metadata and check the data for errors. We are here to help, so let’s start by exploring the data. We see that the quality of data is far from perfect. In fact, the first row contains comments from the anthropologist! To be able to use this data, we need to clean it up a bit.

> Download [`countries.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/countries.csv) to reproduce the examples (right-click and "Save link as").

```bash script
cat countries.csv
```

```python script
with open('countries.csv') as file:
    print(file.read())
```

As we can see, this is data containing information about European countries and their populations. Also, it looks like there are two fields having a relationship based on a country's identifier: neighbor_id is a Foreign Key to id.

## Describing Data

First of all, we're going to describe our dataset. Frictionless uses the powerful [Frictionless Data Specifications](https://specs.frictionlessdata.io/). They are very handy to describe:
- a data table - using [Table Schema](https://specs.frictionlessdata.io/table-schema/)
- a data resource - using [Data Resource](https://specs.frictionlessdata.io/data-resource/)
- a data package - using [Data Package](https://specs.frictionlessdata.io/data-package/)
- and other objects

Let's describe the `countries` table:

```bash script
frictionless describe countries.csv # optionally add --stats to get statistics
```

```python script
from pprint import pprint
from frictionless import describe

resource = describe('countries.csv')
pprint(resource)
```

As we can see, Frictionless was smart enough to understand that the first row contains a comment. It's good, but we still have a few problems:
- we use `n/a` as a missing values marker
- `neighbor_id` must be numerical: let's edit the schema
- `population` must be numerical: setting proper missing values will solve it
- there is a relation between the `id` and `neighbor_id` fields

Let's update our metadata and save it to the disc:


```bash
frictionless describe countries.csv --yaml > countries.resource.yaml
editor countries.resource.yaml
```

> Open this file in your favorite editor and update as it's shown below


```python script
from frictionless import Detector, describe

detector = Detector(field_missing_values=["", "n/a"])
resource = describe("countries.csv", detector=detector)
resource.schema.get_field("neighbor_id").type = "integer"
resource.schema.foreign_keys.append(
    {"fields": ["neighbor_id"], "reference": {"resource": "", "fields": ["id"]}}
)
resource.to_yaml("countries.resource.yaml")
```

Let's see what we have created:

```bash script
cat countries.resource.yaml
```

```python script
with open('countries.resource.yaml') as file:
    print(file.read())
```

It has the same metadata as we saw above but also includes our editing related to missing values and data types. We didn't change all the wrong data types manually because providing proper missing values had fixed it automatically. Now we have a resource descriptor. In the next section, we will show why metadata matters and how to use it.

## Extracting Data

It's time to try extracting our data as a table. As a first naive attempt, we will ignore the metadata we saved on the previous step:

```bash script
frictionless extract countries.csv
```

```python script
from pprint import pprint
from frictionless import extract

rows = extract('countries.csv')
pprint(rows)
```

Actually, it doesn't look terrible, but in reality, data like this is not quite useful:
- it's not possible to export this data e.g., to SQL because integers are mixed with strings
- there is still a basically empty row we don't want to have
- there are some mistakes in the neighbor_id column

Let's use the metadata we save to try extracting data with the help of Frictionless Data specifications:

```bash script
frictionless extract countries.resource.yaml
```

```python script
from pprint import pprint
from frictionless import extract

rows = extract('countries.resource.yaml')
pprint(rows)
```

It's now much better! Numerical fields are numerical fields, and there are no more textual missing values markers. We can't see in the command-line, but missing values are now `None` values in Python, and the data can be e.g., exported to SQL. Although, it's still not ready for being published. In the next section, we will validate it!

## Validating Data

Data validation with Frictionless is as easy as describing or extracting data:

```bash script
frictionless validate countries.csv
```

```python script
from pprint import pprint
from frictionless import validate

report = validate('countries.csv')
pprint(report.flatten(["rowPosition", "fieldPosition", "code"]))
```

Ahh, we had seen that coming. The data is not valid; there are some missing and extra cells. But wait a minute, in the first step, we created the metadata file with more information about our table. We have to use it.

```bash script title="CLI"
frictionless validate countries.resource.yaml
```


```python script
from pprint import pprint
from frictionless import validate

report = validate('countries.resource.yaml')
pprint(report.flatten(["rowPosition", "fieldPosition", "code"]))
```

Now it's even worse, but regarding data validation errors, the more, the better, actually. Thanks to the metadata, we were able to reveal some critical errors:
- the bad data types, i.e. `Ireland` instead of an id
- the bad relation between `id` and `neighbor_id`: we don't have a country with id 22

In the next section, we will clean up the data.

## Transforming Data

We will use metadata to fix all the data type problems automatically. The only two things we need to handle manually:
- France's population
- Germany's neighborhood

```
$ cat > countries.pipeline.yaml <<EOF
steps:
  - type: cell-replace
    fieldName: neighbor_id
    pattern: '22'
    replace: '2'
  - type: cell-replace
    fieldName: population
    pattern: 'n/a'
    replace: '67'
  - type: row-filter
    formula: population
  - type: field-update
    name: neighbor_id
    type: integer
  - type: table-normalize
  - type: table-write
    path: countries.csv
EOF
$ frictionless transform countries.csv --pipeline countries.pipeline.yaml
```

```python
from frictionless import Resource, describe, transform, steps

def clean(resource):
    current = resource.to_copy()

    # Data
    def data():
        with current:
            for row in current.row_stream:
                if row["name"] == "France":
                    row["population"] = 67
                if row["name"] == "Germany":
                    row["neighbor_id"] = 2
                if row["name"]:
                    yield row

    # Meta
    resource.schema = Resource("countries.resource.yaml").schema
    resource.data = data

source = describe("countries.csv")
target = transform(
    source,
    steps=[
        clean,
        steps.table_write(path="countries.csv"),
    ],
)
```

Finally, we've got the cleaned version of our data, which can be exported to a database or published. We have used a CSV as an output format but could have used Excel, JSON, SQL, and others.


```bash
cat countries.csv
```


```python
with open('countries.csv') as file:
    print(file.read())
```

Basically, that's it; now, we have a valid data file and a corresponding metadata file. It can be shared with other people or stored without fear of type errors or other problems making research data not reproducible.

```bash
ls countries.*
```

```python
import os

files = [f for f in os.listdir('.') if os.path.isfile(f) and f.startswith('countries.')]
print(files)
```

In the next articles, we will explore more advanced Frictionless functionality.
