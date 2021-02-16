---
title: Describing Data
---

What does "describing data" mean?

Frictionless is a project based on the [Frictionless Data Specifications](https://specs.frictionlessdata.io/). It's a set of patterns for creating metadata, including Data Package (for datasets), Data Resource (for files), and Table Schema (for tables).

In other words, "describing data" means creating metadata for your data files. The reason for having metadata is simple: usually, data files themselves are not capable of providing enough information. For example, if you have a data table in a CSV format, it misses a few critical pieces of information:
- meaning of the fields e.g., what the `size` field means; is it clothes size or file size
- data types information e.g., is this field a string or an integer
- data constraints e.g., the minimum temperature for your measurements
- data relations e.g., identifiers connection
- and others

```bash title="CLI"
pip install frictionless
```

For a dataset, there is even more information that can be provided, like the general purpose of a dataset, information about data sources, list of authors, and more. Of course, when there are many tabular files, relational rules can be very important. Usually, there are foreign keys ensuring the integrity of the dataset; for example, think of a reference table containing country names and other tables using it as a reference. Data in this form is called "normalized data" and it occurs very often in scientific and other kinds of research.

Now that we have a general understanding of what "describing data" is, we can now articulate why it's important:
- **data validation**: metadata helps to reveal problems in your data during early stages of your workflow
- **data publication**: metadata provides additional information that your data doesn't include

These are not the only positives of having metadata, but they are two of the most important. Please continue reading to learn how Frictionless helps to achieve these advantages by describing your data.

## Describe Functions

The `describe` functions are the main Frictionless tool for describing data. In many cases, this high-level interface is enough for data exploration and other needs.

The frictionless framework provides 4 different `describe` functions in Python:
- `describe`: detects the source type and returns Data Resource or Data Package metadata
- `describe_schema`: always returns Table Schema metadata
- `describe_resource`: always returns Data Resource metadata
- `describe_package`: always returns Data Package metadata

In the command-line, there is only 1 command (`describe`) but there is also a flag to adjust the behavior:

```bash title="CLI"
frictionless describe
frictionless describe --type schema
frictionless describe --type resource
frictionless describe --type package
```

For example, if we want a Data Package descriptor for a single file:


```bash title="CLI"
frictionless describe data/table.csv --type package
```
```yaml
---
metadata: data/table.csv
---

profile: data-package
resources:
    encoding: utf-8
    format: csv
    hashing: md5
    name: table
    path: data/table.csv
    profile: tabular-data-resource
    schema:
      fields:
        - name: id
          type: integer
        - name: name
          type: string
    scheme: file
```

## Describing Schema

Table Schema is a specification for providing a "schema" (similar to a database schema) for tabular data. This information includes the expected data type for each value in a column ("string", "number", "date", etc.), constraints on the value ("this string can only be at most 10 characters long"), and the expected format of the data ("this field should only contain strings that look like email addresses"). Table Schema can also specify relations between tables.

We're going to use this file for the examples in this section. For this guide, we only use CSV files because of their demonstrativeness, but in-general Frictionless can handle data in Excel, JSON, SQL, and many other formats:

```bash title="CLI"
cat data/country-1.csv
```
```csv title="data/country-1.csv"
id,neighbor_id,name,population
1,,Britain,67
2,3,France,67
3,2,Germany,83
4,5,Italy,60
5,4,Spain,47
```

Let's get a Table Schema using the Frictionless framework:

```python title="Python"
from frictionless import describe_schema

schema = describe_schema("data/country-1.csv")
schema.to_yaml("tmp/country.schema-simple.yaml")
```

The high-level functions of Frictionless operate on the dataset and resource levels so we have to use a little bit of Python programming to get the schema information. Below we will show how to use a command-line interface for similar tasks.

```bash title="CLI"
cat tmp/country.schema-simple.yaml
```
```yaml
fields:
  - name: id
    type: integer
  - name: neighbor_id
    type: integer
  - name: name
    type: string
  - name: population
    type: integer
```

As we can see, we were able to infer basic metadata from our data file. But describing data doesn't end here - we can provide additional information that we discussed earlier:

```python title="Python"
from frictionless import describe_schema

schema = describe_schema("data/country-1.csv")
schema.get_field("id").title = "Identifier"
schema.get_field("neighbor_id").title = "Identifier of the neighbor"
schema.get_field("name").title = "Name of the country"
schema.get_field("population").title = "Population"
schema.get_field("population").description = "According to the year 2020's data"
schema.get_field("population").constraints["minimum"] = 0
schema.foreign_keys.append(
    {"fields": ["neighbor_id"], "reference": {"resource": "", "fields": ["id"]}}
)
schema.to_yaml("tmp/country.schema.yaml")
```

Let's break it down:
- we added a title for all the fields
- we added a description to the "Population" field; the year information can be critical to interpret the data
- we set a constraint to the "Population" field because it can't be less than 0
- we added a foreign key saying that "Identifier of the neighbor" should be present in the "Identifier" field


```bash title="CLI"
cat tmp/country.schema.yaml
```
```yaml
fields:
  - name: id
    title: Identifier
    type: integer
  - name: neighbor_id
    title: Identifier of the neighbor
    type: integer
  - name: name
    title: Name of the country
    type: string
  - constraints:
      minimum: 0
    description: According to the year 2020's data
    name: population
    title: Population
    type: integer
foreignKeys:
  - fields:
      - neighbor_id
    reference:
      fields:
        - id
      resource: ''
```

Later we're going to show how to use the schema we created to ensure the validity of your data; in the next few sections, we will focus on Data Resource and Data Package metadata.

To continue learning about table schemas please read:
- [Table Schema Spec](https://specs.frictionlessdata.io/table-schema/)
- [API Reference: Schema](../references/api-reference.md#schema)

## Describing Resource

The Data Resource format describes a data resource such as an individual file or table.
The essence of a Data Resource is a locator for the data it describes.
A range of other properties can be declared to provide a richer set of metadata.

For this section, we will use a file that is slightly more complex to handle. For some reason, cells are separated by the ";" char and there is a comment on the top:


```bash title="CLI"
cat data/country-2.csv
```
```csv title="data/country-2.csv"
# Author: the scientist
id;neighbor_id;name;population
1;;Britain;67
2;3;France;67
3;2;Germany;83
4;5;Italy;60
5;4;Spain;47
```

Let's describe it this time using the command-line interface:

```bash title="CLI"
frictionless describe data/country-2.csv
```
```yaml
---
metadata: data/country-2.csv
---

compression: 'no'
compressionPath: ''
control:
  newline: ''
dialect: {}
encoding: utf-8
scheme: file
format: csv
hashing: md5
name: country-2
path: data/country-2.csv
profile: tabular-data-resource
query: {}
schema:
  fields:
    - name: '# Author: the scientist'
      type: string
```

OK, that's clearly wrong. As we have seen in the "Introductory Guide" Frictionless is capable of inferring some complicated cases' metadata but our table is too unusual for it to automatically infer. We need to manually program it:

```python title="Python"
from frictionless import Schema, describe

resource = describe("data/country-2.csv")
resource.dialect.delimiter = ";"
resource.layout.header_rows = [2]
resource.schema = Schema("tmp/country.schema.yaml")
resource.to_yaml("tmp/country.resource.yaml")
```

So what we did here:
- we set the header rows to be row number 2; as humans, we can easily see that was the proper row
- we set the CSV Delimiter to be ";"
- we reuse the schema we created earlier as the data has the same structure and meaning

```bash title="CLI"
cat tmp/country.resource.yaml
```
```yaml
encoding: utf-8
scheme: file
format: csv
hashing: md5
name: country-2
path: data/country-2.csv
profile: tabular-data-resource
dialect:
  delimiter: ;
layout:
  headerRows:
    - 2
schema:
  fields:
    - name: id
      title: Identifier
      type: integer
    - name: neighbor_id
      title: Identifier of the neighbor
      type: integer
    - name: name
      title: Name of the country
      type: string
    - constraints:
        minimum: 0
      description: According to the year 2020's data
      name: population
      title: Population
      type: integer
  foreignKeys:
    - fields:
        - neighbor_id
      reference:
        fields:
          - id
        resource: ''
```

Our resource metadata includes the schema metadata we created earlier, but it also has:
- general information about the file's schema, format, and compression
- information about CSV Dialect which helps software understand how to read it
- checksum information like hash, bytes, and rows

But the most important difference is that the resource metadata contains the `path` property. This is a conceptual distinction of the Data Resource specification compared to the Table Schema specification. While a Table Schema descriptor can describe a class of data files, a Data Resource descriptor describes only one exact data file, `data/country-2.csv` in our case.

Using programming terminology we could say that:
- Table Schema descriptor is abstract (for a class of files)
- Data Resource descriptor is concrete (for an individual file)

We will show the practical difference in the "Using Metadata" section, but in the next section, we will overview the Data Package specification.

To continue learning about data resources please read:
- [Data Resource Spec](https://specs.frictionlessdata.io/data-resource/)
- [API Reference: Resource](../references/api-reference.md#resource)

## Describing Package

A Data Package consists of:
- Metadata that describes the structure and contents of the package
- Resources such as data files that form the contents of the package
The Data Package metadata is stored in a "descriptor". This descriptor is what makes a collection of data a Data Package. The structure of this descriptor is the main content of the specification below.

In addition to this descriptor, a data package will include other resources such as data files. The Data Package specification does NOT impose any requirements on their form or structure and can, therefore, be used for packaging any kind of data.

The data included in the package may be provided as:
- Files bundled locally with the package descriptor
- Remote resources, referenced by URL
- "Inline" data (see below) which is included directly in the descriptor

For this section, we will use the following files:

```bash title="CLI"
cat data/country-3.csv
```
```csv title="data/country-3.csv"
id,capital_id,name,population
1,1,Britain,67
2,3,France,67
3,2,Germany,83
4,5,Italy,60
5,4,Spain,47
```

```bash title="CLI"
cat data/capital-3.csv
```
```csv title="data/capital-3.csv"
id,name
1,London
2,Berlin
3,Paris
4,Madrid
5,Rome
```

First of all, let's describe our package using the command-line interface. We did it before for a resource but now we're going to use a glob pattern to indicate that there are multiple files:

```bash title="CLI"
frictionless describe data/*-3.csv
```
```yaml
---
metadata: data/capital-3.csv data/country-3.csv
---

profile: data-package
resources:
    encoding: utf-8
    format: csv
    hashing: md5
    name: capital-3
    path: data/capital-3.csv
    profile: tabular-data-resource
    schema:
      fields:
        - name: id
          type: integer
        - name: name
          type: string
    scheme: file
  - encoding: utf-8
    format: csv
    hashing: md5
    name: country-3
    path: data/country-3.csv
    profile: tabular-data-resource
    schema:
      fields:
        - name: id
          type: integer
        - name: capital_id
          type: integer
        - name: name
          type: string
        - name: population
          type: integer
    scheme: file
```

We have already learned about many concepts that are reflected in this metadata. We can see resources, schemas, fields, and other familiar entities. The difference is that this descriptor has information about multiple files which is a popular way of sharing data - in datasets. Very often you have not only one data file but also additional data files, some textual documents e.g. PDF, and others. To package all of these files with the corresponding metadata we use data packages.

Following the pattern that is already familiar to the guide reader, we add some additional metadata:

```python title="Python"
from frictionless import describe

package = describe("data/*-3.csv")
package.title = "Countries and their capitals"
package.description = "The data was collected as a research project"
package.get_resource("country-3").name = "country"
package.get_resource("capital-3").name = "capital"
package.get_resource("country").schema.foreign_keys.append(
    {"fields": ["capital_id"], "reference": {"resource": "capital", "fields": ["id"]}}
)
package.to_yaml("tmp/country.package.yaml")
```

In this case, we add a relation between different files connecting `id` and `capital_id`. Also, we provide dataset-level metadata to explain the purpose of this dataset. We haven't added individual fields' titles and descriptions, but that can be done as it was shown in the "Table Schema" section.

```bash title="CLI"
cat tmp/country.package.yaml
```
```yaml
title: Countries and their capitals
description: The data was collected as a research project
profile: data-package
resources:
  - encoding: utf-8
    format: csv
    hashing: md5
    name: capital
    path: data/capital-3.csv
    profile: tabular-data-resource
    schema:
      fields:
        - name: id
          type: integer
        - name: name
          type: string
    scheme: file
  - encoding: utf-8
    scheme: file
    format: csv
    hashing: md5
    name: country
    path: data/country-3.csv
    profile: tabular-data-resource
    schema:
      fields:
        - name: id
          type: integer
        - name: capital_id
          type: integer
        - name: name
          type: string
        - name: population
          type: integer
      foreignKeys:
        - fields:
            - capital_id
          reference:
            fields:
              - id
            resource: capital
```

The main role of the Data Package descriptor is describing a dataset; as we can see, it includes previously shown descriptors like `schema`, `dialect`, and `resource`. But it would be a mistake to think that Data Package is the least important specification; actually, it completes the Frictionless Data suite making it possible to share and validate not only individual files but also complete datasets.

To continue learning about data resources please read:
- [Data Package Spec](https://specs.frictionlessdata.io/data-package/)
- [API Reference: Package](../references/api-reference.md#package)

##  Metadata Importance

This documentation contains a great deal of information on how to use metadata and why it's vital for your data. In this section, we're going to provide a quick example based on the "Data Resource" section but please read other documents to get the full picture.

Let's get back to this unusual data table:


```bash title="CLI"
cat data/country-2.csv
```
```csv title="data/country-2.csv"
# Author: the scientist
id;neighbor_id;name;population
1;;Britain;67
2;3;France;67
3;2;Germany;83
4;5;Italy;60
5;4;Spain;47
```

As we tried before, by default Frictionless can't properly describe this file so we got something like:

```bash title="CLI"
frictionless describe data/country-2.csv
```
```yaml
---
metadata: data/country-2.csv
---

encoding: utf-8
scheme: file
format: csv
hashing: md5
name: country-2
path: data/country-2.csv
profile: tabular-data-resource
schema:
  fields:
    - name: '# Author: the scientist'
      type: string
```

Trying to extract the data will fail this way:

```bash title="CLI"
frictionless extract data/country-2.csv
```
```
---
data: data/country-2.csv
---

==============================
# Author: the scientist
==============================
id;neighbor_id;name;population
1;;Britain;67
2;3;France;67
3;2;Germany;83
4;5;Italy;60
5;4;Spain;47
==============================
```

This example highlights a really important idea - without metadata many software will not be able to even read this data file. Furthermore, without metadata people cannot understand the purpose of this data. To see how we can use metadata to fix our data, let's now use the `country.resource.yaml` file we created in the "Data Resource" section with Frictionless `extract`:

```bash title="CLI"
frictionless extract tmp/country.resource.yaml --basepath .
```
```
---
data: tmp/country.resource.yaml
---

==  ===========  =======  ==========
id  neighbor_id  name     population
==  ===========  =======  ==========
 1  None         Britain          67
 2            3  France           67
 3            2  Germany          83
 4            5  Italy            60
 5            4  Spain            47
==  ===========  =======  ==========
```

As we can see, the data is now fixed. The metadata we had saved the day! If we explore this data in Python we can discover that it also corrected data types - e.g. `id` is Python's integer not string. We can now export and share this data without any worries.

## Inferring Metadata

Many Frictionless functions infer metadata under the hood such as `describe`, `extract`, and many more. On a lower-level, it's possible to control this process. To see this, let's create a `Resource`.

```python title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource("data/country-1.csv")
pprint(resource)
```
```
{'path': 'data/country-1.csv'}
```

Frictionless always tries to be as explicit as possible. We didn't provide any metadata except for `path` so we got the expected result. But now, we'd like to `infer` additional metadata:

> Note that we use the `stats` argument for the `resource.infer` function. We can ask for stats using CLI with `frictionless describe data/table.csv --stats`


```python title="Python"
resource.infer(stats=True)
pprint(resource)
```
```
{'encoding': 'utf-8',
 'scheme': 'file',
 'format': 'csv',
 'hashing': 'md5',
 'name': 'country-1',
 'path': 'data/country-1.csv',
 'profile': 'tabular-data-resource',
 'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                       {'name': 'neighbor_id', 'type': 'integer'},
                       {'name': 'name', 'type': 'string'},
                       {'name': 'population', 'type': 'integer'}]},
 'stats': {'bytes': 100,
           'fields': 4,
           'hash': '4204f087f328b70c854c03403ab448c4',
           'rows': 5}}
```

The result is really familiar to us already. We have seen it a lot as an output of the `describe` function or command. Basically, that's what this high-level function does under the hood: create a resource and then infer additional metadata.

All the main `Metadata` classes have this method with different available options but with the same conceptual purpose:
- `package.infer`
- `resource.infer`
- `schema.infer`

## Expanding Metadata

By default, Frictionless never adds default values to metadata, for example:

```python title="Python"
from pprint import pprint
from frictionless import describe

resource = describe("data/country-1.csv")
pprint(resource.schema)
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'neighbor_id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
```

Under the hood it, for example, still treats empty strings as missing values because it's the specs' default. We can reveal implicit metadata by expanding it:

```python title="Python"
resource.schema.expand()
pprint(resource.schema)
```
```
{'fields': [{'bareNumber': True,
             'format': 'default',
             'name': 'id',
             'type': 'integer'},
            {'bareNumber': True,
             'format': 'default',
             'name': 'neighbor_id',
             'type': 'integer'},
            {'format': 'default', 'name': 'name', 'type': 'string'},
            {'bareNumber': True,
             'format': 'default',
             'name': 'population',
             'type': 'integer'}],
 'missingValues': ['']}
```

## Transforming Metadata

We have seen this before but let's re-iterate; it's possible to transform core metadata properties using Python's interface:

```python title="Python"
from frictionless import Resource

resource = Resource("tmp/country.resource.yaml")
resource.title = "Countries"
resource.description = "It's a research project"
resource.dialect.delimiter = ";"
resource.layout.header_rows = [2]
resource.to_yaml("tmp/country.resource.yaml")
```

But the Python interface is not our only option. Thanks to the flexibility of the Frictionless Specs, we can add arbitrary metadata to our descriptor. We use dictionary operations to do this:

```python title="Python"
from frictionless import Resource

resource = Resource("tmp/country.resource.yaml")
resource["customKey1"] = "Value1"
resource["customKey2"] = "Value2"
resource.to_yaml("tmp/country.resource.yaml")
```

Let's check it out:

```bash title="CLI"
cat tmp/country.resource.yaml
```
```yaml
customKey1: Value1
customKey2: Value2
title: Countries
description: It's a research project
dialect:
  delimiter: ;
layout:
  headerRows:
    - 2
encoding: utf-8
scheme: file
format: csv
hashing: md5
name: country-2
path: data/country-2.csv
profile: tabular-data-resource
schema:
  fields:
    - name: id
      title: Identifier
      type: integer
    - name: neighbor_id
      title: Identifier of the neighbor
      type: integer
    - name: name
      title: Name of the country
      type: string
    - constraints:
        minimum: 0
      description: According to the year 2020's data
      name: population
      title: Population
      type: integer
  foreignKeys:
    - fields:
        - neighbor_id
      reference:
        fields:
          - id
        resource: ''
```

## Validating Metadata

Metadata validity is an important topic, and we recommend validating your metadata before publishing. For example, let's first make it invalid:

```python title="Python"
from frictionless import Resource

resource = Resource("tmp/country.resource.yaml")
resource["title"] = 1
print(resource.metadata_valid)
print(resource.metadata_errors)
```
```
False
[{'code': 'resource-error', 'name': 'Resource Error', 'tags': ['#general'], 'note': '"1 is not of type \'string\'" at "title" in metadata and at "properties/title/type" in profile', 'message': 'The data resource has an error: "1 is not of type \'string\'" at "title" in metadata and at "properties/title/type" in profile', 'description': 'A validation cannot be processed.'}]
```

We see this error: `'message': 'The data resource has an error: "1 is not of type \'string\'" at "title" in metadata and at "properties/title/type" in profile'` Now, let's fix our resource metadata:

```python title="Python"
from frictionless import Resource

resource = Resource("tmp/country.resource.yaml")
resource["title"] = 'Countries'
print(resource.metadata_valid)
```
```
True
```

You need to check `metadata.metadata_valid` only if you change it manually; Frictionless' high-level functions like `validate` do that on their own.

## Mastering Metadata

The Metadata class is under the hood of many of Frictionless' classes. Let's overview the main `Metadata` features. For a full reference, please read ["API Reference"](../references/api-reference.md). Let's take a look at the Metadata class which is a `dict` subclass:

```text title="Text"
Metadata(dict)
  to_json
  to_yaml
  ---
  metadata_valid
  metadata_errors
  ---
  metadata_attach
  metadata_extract
  metadata_process
  metadata_validate
```

This class exists for subclassing, and here are some important points that will help you work with metadata objects and design and write new metadata classes:
- to bind default values to a property it is possible to use `metadata_attach` (see e.g. the `Schema` class)
- during the initialization a descriptor is processed by `metadata_extract`
- metadata detect any shallow update and call `metadata_process`
- checking for validity or errors will trigger `metadata_validate`
- functions exporting to json and yaml are available by default
- `metadata_profile` can be set to a JSON Schema
- `metadata_Error` can be set to an Error class

## Metadata Classes

Frictionless has many classes that are derived from the `Metadata` class. This means that all of them can be treated as a metadata objects with getters and setters, `to_json` and `to_yaml` function, and other Metadata's API. See ["API Reference"](../references/api-reference.md) for more information about these classes:

- Package
- Resource
- Schema
- Field
- Layout
- Control
- Dialect
- Report
- Pipeline
- Error
- etc
