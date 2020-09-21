# Describing Data

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1eIq1ZTUntJplRxkGHxmqlxZ0zyXCm0wU)



What does "describing data" mean?

Frictionless is a project based on the [Frictionless Data Specifications](https://specs.frictionlessdata.io/). It's a set of patterns for creating metadata, including Data Package (for datasets), Data Resource (for files), and Table Schema (for tables).

In other words, "describing data" means creating metadata for your data files. The reason for having metadata is simple: usually, data files themselves are not capable of providing enough information. For example, if you have a data table in a CSV format, it misses a few critical pieces of information:
- meaning of the fields e.g., what the `size` field means; is it clothes size or file size
- data types information e.g., is this field a string or an integer
- data constraints e.g., the minimum temperature for your measurements
- data relations e.g., identifiers connection
- and others




```bash
! pip install frictionless
```


For a dataset, there is even more information that can be provided like general dataset purpose, information about data sources, list of authors, and many more. Of course, when there are many tabular files, relational rules can be very important. Usually, there are foreign keys ensuring the integrity of the dataset; for example, there is some reference table containing country names and other tables using it as a reference. Data in this form is called "normalized data" and it occurs very often in scientific and another kind of research.

Having a general understanding of what is "data describing", we can now articulate why it's important:
- **data validation**; metadata helps to reveal problems in your data on the early stages of your workflow
- **data publication**; metadata provides additional information that your data can't include

There are not the only two pros of having metadata but they are two the most important. Please continue reading to learn how Frictionless helps to achieve these advantages describing your data.

## Describe Functions

The `describe` functions are the main tool for data describing. In many cases, this high-level interface is enough for data exploration and other needs.

The frictionless framework provides 4 different `describe` functions in Python:
- `describe`: it will detect the source type and return Data Resource or Data Package metadata
- `describe_schema`: it will always return Table Schema metadata
- `describe_resource`: it will always return Data Resource metadata
- `describe_package`: it will always return Data Package metadata

In command-line, there is only 1 command but there is a flag to adjust the behavior:

```bash
$ frictionless describe
$ frictionless describe --source-type schema
$ frictionless describe --source-type resource
$ frictionless describe --source-type package
```

For example, if we want a Data Package descriptor for a single file:



```bash
! wget -q -O table.csv https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv
! cat table.csv
```

    id,name
    1,english
    2,中国人



```bash
! frictionless describe table.csv --source-type package
```

    [metadata] table.csv

    profile: data-package
    resources:
      - bytes: 30
        compression: 'no'
        compressionPath: ''
        dialect: {}
        encoding: utf-8
        format: csv
        hash: 6c2c61dd9b0e9c6876139a449ed87933
        hashing: md5
        name: table
        path: table.csv
        profile: tabular-data-resource
        rows: 2
        schema:
          fields:
            - name: id
              type: integer
            - name: name
              type: string
        scheme: file


### Describing Schema

Table Schema is a specification for providing a "schema" (similar to a database schema) for tabular data. This information includes the expected type of each value in a column ("string", "number", "date", etc.), constraints on the value ("this string can only be at most 10 characters long"), and the expected format of the data ("this field should only contain strings that look like email addresses"). Table Schema can also specify relations between tables.

We're going to use this file for this section examples. For this guide, we use solely CSV files because of their demonstrativeness but in-general Frictionless can handle Excel, JSON, SQL, and many other formats:



```bash
! wget -q -O country-1.csv https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/country-1.csv
! cat country-1.csv
```

    id,neighbor_id,name,population
    1,,Britain,67
    2,3,France,67
    3,2,Germany,83
    4,5,Italy,60
    5,4,Spain,47


Let's get Table Schema using Frictionless framework:



```python
from frictionless import describe_schema

schema = describe_schema("country-1.csv")
schema.to_yaml("country.schema-simple.yaml")
```

The high-level functions of Frictionless operate on dataset and resource levels so we have to use Python a little of Python programming to get schema information. Below we will show how to use a command-line interface for similar tasks.



```bash
! cat country.schema-simple.yaml
```

    fields:
      - name: id
        type: integer
      - name: neighbor_id
        type: integer
      - name: name
        type: string
      - name: population
        type: integer


As we can see, we were able to get infer basic metadata of our data file but describing data doesn't end here, we can  provide additional information we discussed earlier:



```python
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
- we added a foreign key saying that "Identifier of the neighbor" should present in the "Identifier" field



```bash
! cat country.schema.yaml
```

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


Later we're going to show how to use the schema we created to ensure the validity of your data; in the next few sections, we will focus on Data Resource and Data Package metadata.

To continue learning about table schemas please read:
- [Table Schema Spec](https://specs.frictionlessdata.io/table-schema/)
- API Reference: Schema


### Describing Resource

The Data Resource format describes a data resource such as an individual file or table.
The essence of a Data Resource is a locator for the data it describes.
A range of other properties can be declared to provide a richer set of metadata.

For this section, we will use the file that is slightly more complex to handle. For some reason, cells are separated by the ";" char and there is a comment on the top:



```bash
! wget -q -O country-2.csv https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/country-2.csv
! cat country-2.csv
```

    # Author: the scientist
    id;neighbor_id;name;population
    1;;Britain;67
    2;3;France;67
    3;2;Germany;83
    4;5;Italy;60
    5;4;Spain;47


Let's describe it this time using the command-line interface:



```bash
! frictionless describe country-2.csv
```

    [metadata] country-2.csv

    bytes: 124
    compression: 'no'
    compressionPath: ''
    dialect: {}
    encoding: utf-8
    format: csv
    hash: 88e1901235a8cf35da4d28a1cdf415e5
    hashing: md5
    name: country-2
    path: country-2.csv
    profile: tabular-data-resource
    rows: 6
    schema:
      fields:
        - name: '# Author: the scientist'
          type: string
    scheme: file


OK, that's clearly wrong. As we have seen in the "Introductory Guide" Frictionless is capable of inferring some complicated cases' metadata but our table is too weird for it. We need to program it:



```python
from frictionless import describe_resource, Schema

resource = describe_resource("country-2.csv")
resource.dialect.header_rows = [2]
resource.dialect.delimiter = ";"
resource.schema = Schema("country.schema.yaml")
resource.to_yaml("country.resource.yaml")
```

So what we are doing here:
- we set header rows to be row number 2; as humans, we can easily see it
- we set CSV Delimiter to be ";"; this file in not really usual CSV for some reason
- we reuse the schema we created earlier as the data has the same structure and meaning



```bash
! cat country.resource.yaml
```

    bytes: 124
    compression: 'no'
    compressionPath: ''
    dialect:
      delimiter: ;
      headerRows:
        - 2
    encoding: utf-8
    format: csv
    hash: 88e1901235a8cf35da4d28a1cdf415e5
    hashing: md5
    name: country-2
    path: country-2.csv
    profile: tabular-data-resource
    rows: 6
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


Our resource metadata includes the schema metadata we created earlier but also it has:
- general information about the file's schema, format, and compression
- information about CSV Dialect helping software understand how to read it
- checksum information as though hash, bytes, and rows

But the most important difference is that resource metadata contains the `path` property. It conceptually distinct Data Resource specification from Table Schema specification because while a Table Schema descriptor can describe a class of data files, a Data Resource descriptor describes the only one exact data file, `data/country-2.csv` in our case.

Using programming terminology we could say that:
- Table Schema descriptor is abstract (for a class of files)
- Data Resource descriptor is concrete (for an individual file)

We will show the practical difference in the "Using Metadata" section but in the next section, we will overview the Data Package specification.

To continue learning about data resources please read:
- [Data Resource Spec](https://specs.frictionlessdata.io/data-resource/)
- API Reference: Resource


### Describing Package

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



```bash
! wget -q -O country-3.csv https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/country-3.csv
! cat country-3.csv
```

    id,capital_id,name,population
    1,1,Britain,67
    2,3,France,67
    3,2,Germany,83
    4,5,Italy,60
    5,4,Spain,47



```bash
! wget -q -O capital-3.csv https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/capital-3.csv
! cat capital-3.csv
```

    id,name
    1,London
    2,Berlin
    3,Paris
    4,Madrid
    5,Rome


First of all, let's describe our package using the command-line interface. We did it before for a resource but now we're going to use a glob pattern to indicate that there are multiple files:



```bash
! frictionless describe *-3.csv
```

    [metadata] capital-3.csv country-3.csv

    profile: data-package
    resources:
      - bytes: 50
        compression: 'no'
        compressionPath: ''
        dialect: {}
        encoding: utf-8
        format: csv
        hash: e7b6592a0a4356ba834e4bf1c8e8c7f8
        hashing: md5
        name: capital-3
        path: capital-3.csv
        profile: tabular-data-resource
        rows: 5
        schema:
          fields:
            - name: id
              type: integer
            - name: name
              type: string
        scheme: file
      - bytes: 100
        compression: 'no'
        compressionPath: ''
        dialect: {}
        encoding: utf-8
        format: csv
        hash: c0558b91523683483f86f63346d06d81
        hashing: md5
        name: country-3
        path: country-3.csv
        profile: tabular-data-resource
        rows: 5
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


We have already learned about many concepts that are reflected in this metadata. We can see resources, schemas, fields, and other familiar entities. The difference is that this descriptor has information about multiple files which is the most popular way of sharing data - in datasets. Very often you have not only one data file but also additional data files, some textual documents e.g. PDF, and others. To package all of these files with the corresponding metadata we use data packages.

Following the already familiar to the guide's reader pattern, we add some additional metadata:



```python
from frictionless import describe_package

package = describe_package("*-3.csv")
package.title = "Countries and their capitals"
package.description = "The data was collected as a research project"
package.get_resource("country-3").name = "country"
package.get_resource("capital-3").name = "capital"
package.get_resource("country").schema.foreign_keys.append(
    {"fields": ["capital_id"], "reference": {"resource": "capital", "fields": ["id"]}}
)
package.to_yaml("country.package.yaml")
```

In this case, we add a relation between different files connecting `id` and `capital_id`. Also, we provide dataset-level metadata to share with the purpose of this dataset. We haven't added individual fields' titles and description but it can be done as it was shown in the "Table Schema" section.



```bash
! cat country.package.yaml
```

    description: The data was collected as a research project
    profile: data-package
    resources:
      - bytes: 50
        compression: 'no'
        compressionPath: ''
        dialect: {}
        encoding: utf-8
        format: csv
        hash: e7b6592a0a4356ba834e4bf1c8e8c7f8
        hashing: md5
        name: capital
        path: capital-3.csv
        profile: tabular-data-resource
        rows: 5
        schema:
          fields:
            - name: id
              type: integer
            - name: name
              type: string
        scheme: file
      - bytes: 100
        compression: 'no'
        compressionPath: ''
        dialect: {}
        encoding: utf-8
        format: csv
        hash: c0558b91523683483f86f63346d06d81
        hashing: md5
        name: country
        path: country-3.csv
        profile: tabular-data-resource
        rows: 5
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


The main role of the Data Package descriptor is describing a dataset; as we can see, it includes previously shown descriptors as though `schema`, `dialect`, and `resource`. But it's a mistake to think then that Data Package is the least important specification; actually, it completes the Frictionless Data suite making possible sharing and validating not only individual files but complete datasets.

To continue learning about data resources please read:
- [Data Package Spec](https://specs.frictionlessdata.io/data-package/)
- API Reference: Package


## Description Options

The `describe` functions above share the only one common argument:
- `expand`: whether to expand output metadata or not (see "Expanding Metadata")


**Package**

The `describe_package` doesn't accept any additional options.

**Resource**

With the `describe_resource` function you can use as options:
- File Details (see "Extracting Data")
- File Control (see "Extracting Data")
- Table Dialect (see "Extracting Data")
- Table Query (see "Extracting Data")
- Header Options (see "Extracting Data")
- Infer Options

##  Metadata Purpose

This documentation contains a great deal of information on how to use metadata and why it's vital for your data. In this article, we're going to provide a quick example based on the "Data Resource" section but please read other documents to get the full picture.

Let's get back to this exotic data table:



```bash
! cat country-2.csv
```

    # Author: the scientist
    id;neighbor_id;name;population
    1;;Britain;67
    2;3;France;67
    3;2;Germany;83
    4;5;Italy;60
    5;4;Spain;47


As we tried before, by default Frictionless can't properly describe this file so we got something like:



```bash
! frictionless describe country-2.csv
```

    [metadata] country-2.csv

    bytes: 124
    compression: 'no'
    compressionPath: ''
    dialect: {}
    encoding: utf-8
    format: csv
    hash: 88e1901235a8cf35da4d28a1cdf415e5
    hashing: md5
    name: country-2
    path: country-2.csv
    profile: tabular-data-resource
    rows: 6
    schema:
      fields:
        - name: '# Author: the scientist'
          type: string
    scheme: file


Trying to extract the data will fail the same way:



```bash
! frictionless extract country-2.csv
```

    [data] country-2.csv

    # Author: the scientist
    ------------------------------
    id;neighbor_id;name;population
    1;;Britain;67
    2;3;France;67
    3;2;Germany;83
    4;5;Italy;60
    5;4;Spain;47


Basically, that's a really important idea - with not metadata many software will not be able to even read this data file, furthermore, without metadata people can not understand the purpose of this data. Let's now use the `country.resource.yaml` the file we created in the "Data Resource" section:



```bash
! frictionless extract country.resource.yaml
```

    [data] country.resource.yaml

      id    neighbor_id  name       population
    ----  -------------  -------  ------------
       1                 Britain            67
       2              3  France             67
       3              2  Germany            83
       4              5  Italy              60
       5              4  Spain              47


As we can see, it's now fixed. The metadata we'd had saved the day. If we explore this data in Python we can discover that it also correct data types e.g. `id` is Python's integer not string. This fact will allow exporting and sharing this data without any fear.


## Metadata Classes

Frictionless has many classes that is derived from the `Metadata` class. It means that all of them can be treated as a metadata object with getters and setters, `to_json` and `to_yaml` function, and other Metadata's API. See "API Reference" for more information about these classes:

- Package
- Resource
- Schema
- Field
- Control
- Dialect
- Query
- Report
- Pipeline
- Error
- etc



## Inferring Metadata

Many Frictionless functions infer metadata under the hood as though `describe`, `extract`, and many more. On a lower-level, it's possible to control this process. Let's create a `Resource`.



```python
from pprint import pprint
from frictionless import Resource

resource = Resource(path="country-1.csv")
pprint(resource)
```

    {'path': 'country-1.csv'}


Frictionless always tries to be as explicit as possible. We didn't provide any metadata except for `type` so we got the expected result. But now, we'd like to `infer` additional metadata:


```python
resource.infer()
pprint(resource)
```

    {'bytes': 100,
     'compression': 'no',
     'compressionPath': '',
     'dialect': {},
     'encoding': 'utf-8',
     'format': 'csv',
     'hash': '4204f087f328b70c854c03403ab448c4',
     'hashing': 'md5',
     'name': 'country-1',
     'path': 'country-1.csv',
     'profile': 'tabular-data-resource',
     'rows': 5,
     'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                           {'name': 'neighbor_id', 'type': 'integer'},
                           {'name': 'name', 'type': 'string'},
                           {'name': 'population', 'type': 'integer'}]},
     'scheme': 'file'}


The result is really familiar to us already. We have seen it a lot as an output of the `describe` function or command. Basically, that's what this high-level function does under the hood: create a resource and then infer additional metadata.

All main `Metadata` classes have this method with different available options but with the same conceptual purpose:
- `package.infer`
- `resource.infer`
- `schema.infer`

## Expanding Metadata

By default, Frictionless never adds default values to metadata, for example:



```python
from pprint import pprint
from frictionless import describe

resource = describe("country-1.csv")
pprint(resource.schema)
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'neighbor_id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}


Under the hood it, for example, still treats empty string as missing values because it's the specs' default. We can make reveal implicit metadata by expanding it:



```python
resource.schema.expand()
pprint(resource.schema)
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


## Transforming Metadata

We have seen it before but let's re-iterate; it's possible to transform core metadata properties using Python interface:



```python
from frictionless import Resource

resource = Resource("country.resource.yaml")
resource.title = "Countries"
resource.description = "It's a research project"
resource.dialect.header_rows = [2]
resource.dialect.delimiter = ";"
resource.to_yaml("country.resource.yaml")

```

But not only the Python interface is available. Thanks to the flexibility of the Frictionless Specs, we can add arbitrary metadata to our descriptor. We use dictionary operations for it:



```python
from frictionless import Resource

resource = Resource("country.resource.yaml")
resource["customKey1"] = "Value1"
resource["customKey2"] = "Value2"
resource.to_yaml("country.resource.yaml")
```

Let's check it out:


```bash
! cat country.resource.yaml
```

    bytes: 124
    compression: 'no'
    compressionPath: ''
    customKey1: Value1
    customKey2: Value2
    description: It's a research project
    dialect:
      delimiter: ;
      headerRows:
        - 2
    encoding: utf-8
    format: csv
    hash: 88e1901235a8cf35da4d28a1cdf415e5
    hashing: md5
    name: country-2
    path: country-2.csv
    profile: tabular-data-resource
    rows: 6
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


## Validating Metadata

Metadata validity is an important topic so it's recommended to validate your metadata before publishing. For example, let's make it invalid:




```python
from frictionless import Resource

resource = Resource("country.resource.yaml")
resource["title"] = 1
print(resource.metadata_valid)
print(resource.metadata_errors)
```

    False
    [{'code': 'resource-error', 'name': 'Resource Error', 'tags': ['#general'], 'note': '"1 is not of type \'string\'" at "title" in metadata and at "properties/title/type" in profile', 'message': 'The data resource has an error: "1 is not of type \'string\'" at "title" in metadata and at "properties/title/type" in profile', 'description': 'A validation cannot be processed.'}]


Let's fix our resource metadata:



```python
from frictionless import Resource

resource = Resource("country.resource.yaml")
resource["title"] = 'Countries'
print(resource.metadata_valid)
```

    True


You need to check `metadata.metadata_valid` only if you change it by hands; the available high-level functions like `validate` do it on their own.


## Mastering Metadata

Metadata class is under the hood of many of Frictionless' classes. Let's overview main `Metadata` features. For a full reference, please read "API Reference". Let's take a look at the Metadata class which is a `dict` subclass:

```text
Metadata(dict)
  metadata_attach
  metadata_extract
  metadata_process
  metadata_validate
  ---
  metadata_valid
  metadata_errors
  ---
  to_json
  to_yaml
```

This class exists for subclassing and here is important points that will help to work with metadata objects and design and write new metadata classes:
- to bind default values to a property it's possible to use `metadata_attach` (see e.g. the `Schema` class)
- during the initialization a descriptor is processed by `metadata_extract`
- metadata detect any shallow update and call `metadata_process`
- checking for validity or errors will trigger `metadata_validate`
- functions exporting to json and yaml are available be default
- `metadata_profile` can be set to a JSON Schema
- `metadata_Error` can be set to an Error class

## Infer Options

Let's explore some handy options to customize the infer process. All of them are available in some form for all the functions above and for different invocation types: in Python, in CLI, or for a REST server.


**Infer Type**

This option allows manually setting all the field types to a given type. It's useful when you need to skip datacasting (setting `any` type) or have everything as a string (setting `string` type):



```bash
! frictionless describe country-1.csv --infer-type string
```

    [metadata] country-1.csv

    bytes: 100
    compression: 'no'
    compressionPath: ''
    dialect: {}
    encoding: utf-8
    format: csv
    hash: 4204f087f328b70c854c03403ab448c4
    hashing: md5
    name: country-1
    path: country-1.csv
    profile: tabular-data-resource
    rows: 5
    schema:
      fields:
        - name: id
          type: string
        - name: neighbor_id
          type: string
        - name: name
          type: string
        - name: population
          type: string
    scheme: file


**Infer Names**

Sometimes you don't want to use existent header row to compose field names. It's possible to provide custom names:



```python
from frictionless import describe

resource = describe("country-1.csv", infer_names=["f1", "f2", "f3", "f4"])
print(resource.schema.field_names)
```

    ['f1', 'f2', 'f3', 'f4']


**Infer Volume**

By default, Frictionless will use the first 100 rows to detect field types. This can be customized. The following code will be slower but the result can be more accurate



```python
from frictionless import describe

resource = describe("country-1.csv", infer_volume=1000)
```

**Infer Confidence**

By default, Frictionless uses 0.9 (90%) confidence level for data types detection. It means that it there are 9 integers in a field and one string it will be inferred as an integer. If you want a guarantee that an inferred schema will conform to the data you can set it to 1 (100%):



```python
from frictionless import describe

resource = describe("country-1.csv", infer_confidence=1)
```

**Infer Missing Values**

Missing Values is an important concept in data description. It provides information about what cell values should be considered as nulls. We can customize the defaults:



```python
from pprint import pprint
from frictionless import describe

resource = describe("country-1.csv", infer_missing_values=["", "67"])
pprint(resource.schema.missing_values)
pprint(resource.read_rows())
```

    ['', '67']
    [Row([('id', 1),
          ('neighbor_id', None),
          ('name', 'Britain'),
          ('population', None)]),
     Row([('id', 2), ('neighbor_id', 3), ('name', 'France'), ('population', None)]),
     Row([('id', 3), ('neighbor_id', 2), ('name', 'Germany'), ('population', 83)]),
     Row([('id', 4), ('neighbor_id', 5), ('name', 'Italy'), ('population', 60)]),
     Row([('id', 5), ('neighbor_id', 4), ('name', 'Spain'), ('population', 47)])]


As we can see, the textual values equal to "67" are now considered nulls. Usually, it's handy when you have data with values like: '-', 'n/a', and similar.
