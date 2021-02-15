---
title: Introduction Guide
---

Let's say we have a few raw data files. It's been just collected by the data researchers, and the quality of data is still far from perfect. In fact, they haven't even removed the comments from the first row!


```bash title="CLI"
$ cat data/countries.csv
```
```
# clean this data!
id,neighbor_id,name,population
1,Ireland,Britain,67
2,3,France,n/a,find the population
3,22,Germany,83
4,,Italy,60
5
```

As we can see, it's a data containing information about European countries and their populations. Also, it's easy to notice that there are two fields having a relationship based on a country's identifier: neighbor_id is a Foreign Key to id.

## Describing Data

First of all, we're going to describe our dataset. Frictionless uses powerful [Frictionless Data Specifications](https://specs.frictionlessdata.io/). They are very handy to describe:
- a data table - [Table Schema](https://specs.frictionlessdata.io/table-schema/)
- a data resource - [Data Resource](https://specs.frictionlessdata.io/data-resource/)
- a data package - [Data Package](https://specs.frictionlessdata.io/data-package/)
- and other objects

Let's describe the `countries` table:

```bash title="CLI"
$ frictionless describe data/countries.csv
$ frictionless describe data/countries.csv --stats # to get also stats
```

```yaml
---
metadata: data/countries.csv
---

path: data/countries.csv
encoding: utf-8
format: csv
scheme: file
hashing: md5
name: countries
profile: tabular-data-resource
layout:
  headerRows:
    - 2
schema:
  fields:
    - name: id
      type: integer
    - name: neighbor_id
      type: string
    - name: name
      type: string
    - name: population
      type: string
 ```

As we can see, Frictionless was smart enough to understand that the first row contains a comment. It's good, but we still have a few problems:
- we use `n/a` as a missing values marker
- `neighbor_id` must be numerical: let's edit the schema
- `population` must be numerical: setting proper missing values will solve it
- there is a relation between the `id` and `neighbor_id` fields

Let's update our metadata and save it to the disc:

```python title="Python"
from frictionless import Detector, describe

detector = Detector(field_missing_values=["", "n/a"])
resource = describe("data/countries.csv", detector=detector)
resource.schema.get_field("neighbor_id").type = "integer"
resource.schema.foreign_keys.append(
    {"fields": ["neighbor_id"], "reference": {"resource": "", "fields": ["id"]}}
)
resource.to_yaml("tmp/countries.resource.yaml")
```

Let's see what we have created:

```bash title="CLI"
$ cat tmp/countries.resource.yaml
```
```yaml
encoding: utf-8
format: csv
scheme: file
hashing: md5
name: countries
path: data/countries.csv
profile: tabular-data-resource
layout:
  headerRows:
    - 2
schema:
  fields:
    - name: id
      type: integer
    - name: neighbor_id
      type: integer
    - name: name
      type: string
    - name: population
      type: integer
  foreignKeys:
    - fields:
        - neighbor_id
      reference:
        fields:
          - id
        resource: ''
  missingValues:
    - ''
    - n/a
```

It has the same metadata as we saw above but also includes our editing related to missing values and data types. We didn't change all the wrong data types manually because providing proper missing values had fixed it automatically. Now we have a resource descriptor. In the next section, we will show why metadata matters and how to use it.

## Extracting Data

It's time to try extracting our data as a table. As a first naive attempt, we will ignore the metadata we saved on the previous step:


```bash title="CLI"
$ frictionless extract data/countries.csv
```
```
---
data: data/countries.csv
---

==  ===========  =======  ==========
id  neighbor_id  name     population
==  ===========  =======  ==========
 1  Ireland      Britain  67
 2  3            France   n/a
 3  22           Germany  83
 4  None         Italy    60
 5  None         None     None
==  ===========  =======  ==========
```

Actually, it doesn't look terrible, but in reality, data like this is not quite useful:
- it's not possible to export this data e.g., to SQL because integers are mixed with strings
- there is still a basically empty row we don't want to have
- there is a clear mistake in Germany's neighborhood!

Let's use the metadata we save to try extracting data with the help of Frictionless Data specifications:

```bash title="CLI"
$ frictionless extract tmp/countries.resource.yaml --basepath .
```
```
---
data: tmp/countries.resource.yaml
---

==  ===========  =======  ==========
id  neighbor_id  name     population
==  ===========  =======  ==========
 1  None         Britain          67
 2            3  France   None
 3           22  Germany          83
 4  None         Italy            60
 5  None         None     None
==  ===========  =======  ==========
```

It's now much better! Numerical fields are numerical fields, and there are no more textual missing values markers. We can't see in the command-line, but missing values are now `None` values in Python, and the data can be e.g., exported to SQL. Although, it's still not ready for being published. In the next section, we will validate it!

## Validating Data

Data validation with Frictionless is as easy as describing or extracting data:

```bash title="CLI"
$ frictionless validate data/countries.csv
```
```
---
invalid: data/countries.csv
---

===  =====  ============  =============================================================================
row  field  code          message
===  =====  ============  =============================================================================
  4      5  extra-cell    Row at position "4" has an extra value in field at position "5"
  7      2  missing-cell  Row at position "7" has a missing cell in field "neighbor_id" at position "2"
  7      3  missing-cell  Row at position "7" has a missing cell in field "name" at position "3"
  7      4  missing-cell  Row at position "7" has a missing cell in field "population" at position "4"
===  =====  ============  =============================================================================
```

Ahh, we had seen that coming. The data is not valid; there are some missing and extra cells. But wait a minute, in the first step, we created the metadata file with more information about our table. We have to use it.

```bash title="CLI"
$ frictionless validate tmp/countries.resource.yaml --basepath .
```
```
---
invalid: ./data/countries.csv
---

===  =====  =================  ==================================================================================================================================
row  field  code               message
===  =====  =================  ==================================================================================================================================
  3      2  type-error         The cell "Ireland" in row at position "3" and field "neighbor_id" at position "2" has incompatible type: type is "integer/default"
  4      5  extra-cell         Row at position "4" has an extra value in field at position "5"
  5  None   foreign-key-error  The row at position "5" does not conform to the foreign key constraint: not found in the lookup table
  7      2  missing-cell       Row at position "7" has a missing cell in field "neighbor_id" at position "2"
  7      3  missing-cell       Row at position "7" has a missing cell in field "name" at position "3"
  7      4  missing-cell       Row at position "7" has a missing cell in field "population" at position "4"
===  =====  =================  ==================================================================================================================================
```

Now it's even worse, but regarding data validation errors, the more, the better, actually. Thanks to the metadata, we were able to reveal some critical errors:
- the bad data types, i.e. `Ireland` instead of an id
- the bad relation between `id` and `neighbor_id`: we don't have a country with id 22

In the next section, we will clean up the data.

## Transforming Data

> Currently, the transform capabilities are under construction. For now, we will use Python programming for data cleaning.

We will use metadata to fix all the data type problems automatically. The only two things we need to handle manually:
- France's population
- Germany's neighborhood

```python title="Python"
from frictionless import Resource, Table

def source():
    resource = Resource("tmp/countries.resource.yaml", basepath='.')
    for row in resource.read_rows():
        if row["name"] == "France":
            row["population"] = 67
        if row["name"] == "Germany":
            row["neighbor_id"] = 2
        if row["name"]:
            yield row

with Table(source) as table:
    table.write("tmp/countries-cleaned.csv")
```

Finally, we've got the cleaned version of our data, which can be exported to a database or published. We have used a CSV as an output format but could have used Excel, JSON, SQL, and others.

```bash title="CLI"
$ cat tmp/countries-cleaned.csv
```
```
id,neighbor_id,name,population
1,,Britain,67
2,3,France,67
3,2,Germany,83
4,,Italy,60
```

We also need to update our metadata file:

```python title="Python"
from frictionless import Resource, describe

source = Resource("tmp/countries.resource.yaml")
target = describe("tmp/countries-cleaned.csv")
target.schema.foreign_keys = source.schema.foreign_keys
target.to_yaml("tmp/countries-cleaned.resource.yaml")
```

After running this script our metadata will be:

```bash title="CLI"
$ cat tmp/countries-cleaned.resource.yaml
```
```yaml
encoding: utf-8
format: csv
scheme: file
hashing: md5
name: countries-cleaned
path: tmp/countries-cleaned.csv
profile: tabular-data-resource
schema:
  fields:
    - name: id
      type: integer
    - name: neighbor_id
      type: any
    - name: name
      type: string
    - name: population
      type: integer
  foreignKeys:
    - fields:
        - neighbor_id
      reference:
        fields:
          - id
        resource: ''
```

Basically, that's it; now, we have a valid data file and a corresponding metadata file. It can be shared with other people or stored without fear of type errors or other problems making data research not reproducible.


```bash title="CLI"
$ ls -la tmp/countries-cleaned.csv tmp/countries-cleaned.resource.yaml
```
```
-rw------- 1 roll roll  91 дек  2 11:42 tmp/countries-cleaned.csv
-rw------- 1 roll roll 926 дек  2 11:41 tmp/countries-cleaned.resource.yaml
```

In the next articles, we will explore more advanced Frictionless' functionality.
