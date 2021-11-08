---
title: Describing Data
prepare:
  - cp data/table.csv table.csv
  - cp data/country-1.csv country-1.csv
  - cp data/country-2.csv country-2.csv
  - cp data/country-3.csv country-3.csv
  - cp data/capital-3.csv capital-3.csv
cleanup:
  - rm table.csv
  - rm country-1.csv
  - rm country-2.csv
  - rm country-3.csv
  - rm capital-3.csv
  - rm country.schema.yaml
  - rm country.resource.yaml
  - rm country.package.yaml
---

> This guide assumes basic familiarity with the Frictionless Framework. To learn more, please read the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction) and [Quick Start](https://framework.frictionlessdata.io/docs/guides/quick-start). Also, this guide is meant to be read in order from top to bottom, and reuses examples throughout the text. You can use the menu to skip sections, but please note that you might need to run code from earlier sections to make all the examples work.

In Frictionless terms, "Describing data" means creating metadata for your data files. Having metadata is important because data files by themselves usually do not provide enough information to fully understand the data. For example, if you have a data table in a CSV format without metadata, you are missing a few critical pieces of information:
- the meaning of the fields e.g., what the `size` field means (does that field mean geographic size? Or does it refer to the size of the file?)
- data type information e.g., is this field a string or an integer?
- data constraints e.g., the minimum temperature for your measurements
- data relations e.g., identifier connections
- and others

For a dataset, there is even more information that can be provided, like the general purpose of a dataset, information about data sources, list of authors, and more. Also, when there are many tabular files, relational rules can be very important. Usually, there are foreign keys ensuring the integrity of the dataset; for example, think of a reference table containing country names and other data tables using it as a reference. Data in this form is called "normalized data" and it occurs very often in scientific and other kinds of research.

Now that we have a general understanding of what "describing data" is, we can discuss why it is important:
- **data validation**: metadata helps to reveal problems in your data during early stages of your workflow
- **data publication**: metadata provides additional information that your data doesn't include

These are not the only positives of having metadata, but they are two of the most important. Please continue reading to learn how Frictionless helps to achieve these advantages by describing your data. This guide will discuss the main `describe` functions (`describe`, `describe_schema`, `describe_resource`, `describe_package`) and will then go into more detail about how to create and edit metadata in Frictionless.

For the following examples, you will need to have Frictionless installed. See our [Quick Start Guide](https://framework.frictionlessdata.io/docs/guides/quick-start) if you need help.

```bash title="CLI"
pip install frictionless
```

## Describe Functions

The `describe` functions are the main Frictionless tool for describing data. In many cases, this high-level interface is enough for data exploration and other needs.

The frictionless framework provides 4 different `describe` functions in Python:
- `describe`: detects the source type and returns Data Resource or Data Package metadata
- `describe_schema`: always returns Table Schema metadata
- `describe_resource`: always returns Data Resource metadata
- `describe_package`: always returns Data Package metadata

As described in more detail in the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction), a resource is a single file, such as a data file, and a package is a set of files, such as a data file and a schema.

In the command-line, there is only 1 command (`describe`) but there is also a flag to adjust the behavior:

```bash title="CLI"
frictionless describe your-table.csv
frictionless describe your-table.csv --type schema
frictionless describe your-table.csv --type resource
frictionless describe your-table.csv --type package
```

Please take into account that file names might be used by Frictionless to detect a metadata type for data extraction or validation. It's recommended to use corresponding suffixes when you save your metadata to the disk. For example, you might name your Table Schema as `table.schema.yaml`, Data Resource as `table.resource.yaml`, and Data Package as `table.package.yaml`. If there is no hint in the file name Frictionless will assume that it's a resource descriptor by default.

For example, if we want a Data Package descriptor for a single file:

> Download [`table.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv) to reproduce the examples (right-click and "Save link as").

```bash script title="CLI"
frictionless describe table.csv --type package
```
```yaml
# --------
# metadata: table.csv
# --------

profile: data-package
resources:
  - encoding: utf-8
    format: csv
    hashing: md5
    name: table
    path: table.csv
    profile: tabular-data-resource
    schema:
      fields:
        - name: id
          type: integer
        - name: name
          type: string
    scheme: file
```

## Describing a Schema

Table Schema is a specification for providing a "schema" (similar to a database schema) for tabular data. This information includes the expected data type for each value in a column ("string", "number", "date", etc.), constraints on the value ("this string can only be at most 10 characters long"), and the expected format of the data ("this field should only contain strings that look like email addresses"). Table Schema can also specify relations between data tables.

We're going to use this file for the examples in this section. For this guide, we only use CSV files because of their demonstrativeness, but in general Frictionless can handle data in Excel, JSON, SQL, and many other formats:

> Download [`country-1.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/country-1.csv) to reproduce the examples (right-click and "Save link as").

```bash script title="CLI"
cat country-1.csv
```
```csv title="country-1.csv"
id,neighbor_id,name,population
1,,Britain,67
2,3,France,67
3,2,Germany,83
4,5,Italy,60
5,4,Spain,47
```

Let's get a Table Schema using the Frictionless framework (note: this example uses YAML for the schema format, but Frictionless also supports JSON format):

```python script title="Python"
from frictionless import describe_schema

schema = describe_schema("country-1.csv")
schema.to_yaml("country.schema.yaml") # use schema.to_json for JSON
```

The high-level functions of Frictionless operate on the dataset and resource levels so we have to use a little bit of Python programming to get the schema information. Below we will show how to use a command-line interface for similar tasks.

```bash script title="CLI"
cat country.schema.yaml
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

```python script title="Python"
from frictionless import describe_schema

schema = describe_schema("country-1.csv")
schema.get_field("id").title = "Identifier"
schema.get_field("neighbor_id").title = "Identifier of the neighbor"
schema.get_field("name").title = "Name of the country"
schema.get_field("population").title = "Population"
schema.get_field("population").description = "According to the year 2020's data"
schema.get_field("population").constraints["minimum"] = 0
schema.foreign_keys.append(
    {"fields": ["neighbor_id"], "reference": {"resource": "", "fields": ["id"]}}
)
schema.to_yaml("country.schema.yaml")
```

Let's break it down:
- we added a title for all the fields
- we added a description to the "Population" field; the year information can be critical to interpret the data
- we set a constraint to the "Population" field because it can't be less than 0
- we added a foreign key saying that "Identifier of the neighbor" should be present in the "Identifier" field

```bash script title="CLI"
cat country.schema.yaml
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

## Describing a Resource

The Data Resource format describes a data resource such as an individual file or data table.
The essence of a Data Resource is a path to the data file it describes.
A range of other properties can be declared to provide a richer set of metadata including Table Schema for tabular data.

For this section, we will use a file that is slightly more complex to handle. In this example, cells are separated by the ";" character and there is a comment on the top:

> Download [`country-2.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/country-2.csv) to reproduce the examples (right-click and "Save link as").

```bash title="CLI"
cat country-2.csv
```
```csv title="country-2.csv"
# Author: the scientist
id;neighbor_id;name;population
1;;Britain;67
2;3;France;67
3;2;Germany;83
4;5;Italy;60
5;4;Spain;47
```

Let's describe it this time using the command-line interface:

```bash script title="CLI"
frictionless describe country-2.csv
```
```yaml
# --------
# metadata: country-2.csv
# --------

encoding: utf-8
format: csv
hashing: md5
name: country-2
path: country-2.csv
profile: tabular-data-resource
schema:
  fields:
    - name: '# Author: the scientist'
      type: string
scheme: file
```

OK, that looks wrong -- for example, the schema has only inferred one field, and that field does not seem correct either. As we have seen in the "Introductory Guide" Frictionless is capable of inferring some complicated cases' metadata but our data table is too complex for it to automatically infer. We need to manually program it:

```python script title="Python"
from frictionless import Schema, describe

resource = describe("country-2.csv")
resource.dialect.delimiter = ";"
resource.layout.header_rows = [2]
resource.schema = Schema("country.schema.yaml")
resource.to_yaml("country.resource.yaml")
```

So what we did here:
- we set the header rows to be row number 2; as humans, we can easily see that was the proper row
- we set the CSV Delimiter to be ";"
- we reuse the schema we created [earlier](#describing-a-schema) as the data has the same structure and meaning

```bash script title="CLI"
cat country.resource.yaml
```
```yaml
dialect:
  delimiter: ;
encoding: utf-8
format: csv
hashing: md5
layout:
  headerRows:
    - 2
name: country-2
path: country-2.csv
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
scheme: file
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

## Describing a Package

A Data Package consists of:
- Metadata that describes the structure and contents of the package
- Resources such as data files that form the contents of the package

The Data Package metadata is stored in a "descriptor". This descriptor is what makes a collection of data a Data Package. The structure of this descriptor is the main content of the specification below.

In addition to this descriptor, a data package will include other resources such as data files. The Data Package specification does NOT impose any requirements on their form or structure and can, therefore, be used for packaging any kind of data.

The data included in the package may be provided as:
- Files bundled locally with the package descriptor
- Remote resources, referenced by URL (see the [schemes tutorial](https://framework.frictionlessdata.io/docs/tutorials/schemes/local-tutorial) for more information about supported URLs)
- "Inline" data (see below) which is included directly in the descriptor

For this section, we will use the following files:

> Download [`country-3.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/country-3.csv) to reproduce the examples (right-click and "Save link as")

```bash script title="CLI"
cat country-3.csv
```
```csv title="country-3.csv"
id,capital_id,name,population
1,1,Britain,67
2,3,France,67
3,2,Germany,83
4,5,Italy,60
5,4,Spain,47
```

> Download [`capital-3.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/capital-3.csv) to reproduce the examples (right-click and "Save link as").

```bash script title="CLI"
cat capital-3.csv
```
```csv title="capital-3.csv"
id,name
1,London
2,Berlin
3,Paris
4,Madrid
5,Rome
```

First of all, let's describe our package using the command-line interface. We did it before for a resource but now we're going to use a glob pattern to indicate that there are multiple files:

```bash script title="CLI"
frictionless describe *-3.csv
```
```yaml
# --------
# metadata: capital-3.csv country-3.csv
# --------

profile: data-package
resources:
  - encoding: utf-8
    format: csv
    hashing: md5
    name: capital-3
    path: capital-3.csv
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
    path: country-3.csv
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

```python script title="Python"
from frictionless import describe

package = describe("*-3.csv")
package.title = "Countries and their capitals"
package.description = "The data was collected as a research project"
package.get_resource("country-3").name = "country"
package.get_resource("capital-3").name = "capital"
package.get_resource("country").schema.foreign_keys.append(
    {"fields": ["capital_id"], "reference": {"resource": "capital", "fields": ["id"]}}
)
package.to_yaml("country.package.yaml")
```

In this case, we add a relation between different files connecting `id` and `capital_id`. Also, we provide dataset-level metadata to explain the purpose of this dataset. We haven't added individual fields' titles and descriptions, but that can be done as it was shown in the "Table Schema" section.

```bash script title="CLI"
cat country.package.yaml
```
```yaml
description: The data was collected as a research project
profile: data-package
resources:
  - encoding: utf-8
    format: csv
    hashing: md5
    name: capital
    path: capital-3.csv
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
    name: country
    path: country-3.csv
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
    scheme: file
title: Countries and their capitals
```

The main role of the Data Package descriptor is describing a dataset; as we can see, it includes previously shown descriptors like `schema`, `dialect`, and `resource`. But it would be a mistake to think that Data Package is the least important specification; actually, it completes the Frictionless Data suite making it possible to share and validate not only individual files but also complete datasets.

To continue learning about data resources please read:
- [Data Package Spec](https://specs.frictionlessdata.io/data-package/)
- [API Reference: Package](../references/api-reference.md#package)

## Metadata Importance

This documentation contains a great deal of information on how to use metadata and why it's vital for your data. In this section, we're going to provide a quick example based on the "Data Resource" section but please read other documents to get the full picture.

Let's get back to this complex data table:

```bash script title="CLI"
cat country-2.csv
```
```csv title="country-2.csv"
# Author: the scientist
id;neighbor_id;name;population
1;;Britain;67
2;3;France;67
3;2;Germany;83
4;5;Italy;60
5;4;Spain;47
```

As we tried before, by default Frictionless can't properly describe this file so we got something like:

```bash script title="CLI"
frictionless describe country-2.csv
```
```yaml
# --------
# metadata: country-2.csv
# --------

encoding: utf-8
format: csv
hashing: md5
name: country-2
path: country-2.csv
profile: tabular-data-resource
schema:
  fields:
    - name: '# Author: the scientist'
      type: string
scheme: file
```

Trying to extract the data will fail this way:

```bash script title="CLI"
frictionless extract country-2.csv
```
```
# ----
# data: country-2.csv
# ----

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

```bash script title="CLI"
frictionless extract country.resource.yaml
```
```
# ----
# data: country.resource.yaml
# ----

==  ===========  =======  ==========
id  neighbor_id  name     population
==  ===========  =======  ==========
 1               Britain          67
 2            3  France           67
 3            2  Germany          83
 4            5  Italy            60
 5            4  Spain            47
==  ===========  =======  ==========
```

As we can see, the data is now fixed. The metadata we had saved the day! If we explore this data in Python we can discover that it also corrected data types - e.g. `id` is Python's integer not string. We can now export and share this data without any worries.

## Inferring Metadata

> Many Frictionless Framework's classes are metadata classes as though Schema, Resource, or Package. All the sections below are applicable for all these classes. You can read about the base Metadata class in more detail in [API Reference](../references/api-reference.md#metadata).

Many Frictionless functions infer metadata under the hood such as `describe`, `extract`, and many more. On a lower-level, it's possible to control this process. To see this, let's create a `Resource`.

```python script title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource("country-1.csv")
pprint(resource)
```
```
{'path': 'country-1.csv'}
```

Frictionless always tries to be as explicit as possible. We didn't provide any metadata except for `path` so we got the expected result. But now, we'd like to `infer` additional metadata:

> Note that we use the `stats` argument for the `resource.infer` function. We can ask for stats using CLI with `frictionless describe data/table.csv --stats`.

```python title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource("country-1.csv")
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

For more advanced detection options, please read the [Detector Guide](framework/detector-guide.md)

## Expanding Metadata

By default, Frictionless never adds default values to metadata, for example:

```python script title="Python"
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

```python script title="Python"
from pprint import pprint
from frictionless import describe

resource = describe("data/country-1.csv")
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

```python script title="Python"
from frictionless import Resource

resource = Resource("country.resource.yaml")
resource.title = "Countries"
resource.description = "It's a research project"
resource.dialect.delimiter = ";"
resource.layout.header_rows = [2]
resource.to_yaml("country.resource.yaml")
```

But the Python interface is not our only option. Thanks to the flexibility of the Frictionless Specs, we can add arbitrary metadata to our descriptor. We use dictionary operations to do this:

```python script title="Python"
from frictionless import Resource

resource = Resource("country.resource.yaml")
resource["customKey1"] = "Value1"
resource["customKey2"] = "Value2"
resource.to_yaml("country.resource.yaml")
```

Let's check it out:

```bash script title="CLI"
cat country.resource.yaml
```
```yaml
customKey1: Value1
customKey2: Value2
description: It's a research project
dialect:
  delimiter: ;
encoding: utf-8
format: csv
hashing: md5
layout:
  headerRows:
    - 2
name: country-2
path: country-2.csv
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
scheme: file
title: Countries
```

## Validating Metadata

Metadata validity is an important topic, and we recommend validating your metadata before publishing. For example, let's first make it invalid:

```python script title="Python"
from frictionless import Resource

resource = Resource("country.resource.yaml")
resource["title"] = 1
print(resource.metadata_valid)
print(resource.metadata_errors)
```
```
False
[{'code': 'resource-error', 'name': 'Resource Error', 'tags': [], 'note': '"1 is not of type \'string\'" at "title" in metadata and at "properties/title/type" in profile', 'message': 'The data resource has an error: "1 is not of type \'string\'" at "title" in metadata and at "properties/title/type" in profile', 'description': 'A validation cannot be processed.'}]
```

We see this error: `'message': 'The data resource has an error: "1 is not of type \'string\'" at "title" in metadata and at "properties/title/type" in profile'` Now, let's fix our resource metadata:

```python script title="Python"
from frictionless import Resource

resource = Resource("country.resource.yaml")
resource["title"] = 'Countries'
print(resource.metadata_valid)
```
```
True
```

You need to check `metadata.metadata_valid` only if you change it manually; Frictionless' high-level functions like `validate` do that on their own.
