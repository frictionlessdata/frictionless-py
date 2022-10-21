---
script:
  basepath: data
---

# Describing Data

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

These are not the only positives of having metadata, but they are two of the most important. Please continue reading to learn how Frictionless helps to achieve these advantages by describing your data. This guide will discuss the main `describe` functions (`describe`, `Schema.describe`, `Resource.describe`, `Package.describe`) and will then go into more detail about how to create and edit metadata in Frictionless.

For the following examples, you will need to have Frictionless installed. See our [Quick Start Guide](https://framework.frictionlessdata.io/docs/guides/quick-start) if you need help.

```bash tabs=CLI
pip install frictionless
```

## Describe Functions

The `describe` functions are the main Frictionless tool for describing data. In many cases, this high-level interface is enough for data exploration and other needs.

The frictionless framework provides 4 different `describe` functions in Python:
- `describe`: detects the source type and returns Data Resource or Data Package metadata
- `Schema.describe`: always returns Table Schema metadata
- `Resource.describe`: always returns Data Resource metadata
- `Package.describe`: always returns Data Package metadata

As described in more detail in the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction), a resource is a single file, such as a data file, and a package is a set of files, such as a data file and a schema.

In the command-line, there is only 1 command (`describe`) but there is also a flag to adjust the behavior:

```bash tabs=CLI
frictionless describe your-table.csv
frictionless describe your-table.csv --type schema
frictionless describe your-table.csv --type resource
frictionless describe your-table.csv --type package
```

Please take into account that file names might be used by Frictionless to detect a metadata type for data extraction or validation. It's recommended to use corresponding suffixes when you save your metadata to the disk. For example, you might name your Table Schema as `table.schema.yaml`, Data Resource as `table.resource.yaml`, and Data Package as `table.package.yaml`. If there is no hint in the file name Frictionless will assume that it's a resource descriptor by default.

For example, if we want a Data Package descriptor for a single file:

> Download [`table.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/main/data/table.csv) to reproduce the examples (right-click and "Save link as").

```bash script tabs=CLI output=yaml
frictionless describe table.csv --type package
```

```python script tabs=Python output=yaml
from frictionless import describe

package = describe("table.csv", type="package")
print(package.to_yaml())
```

## Describing a Schema

Table Schema is a specification for providing a "schema" (similar to a database schema) for tabular data. This information includes the expected data type for each value in a column ("string", "number", "date", etc.), constraints on the value ("this string can only be at most 10 characters long"), and the expected format of the data ("this field should only contain strings that look like email addresses"). Table Schema can also specify relations between data tables.

We're going to use this file for the examples in this section. For this guide, we only use CSV files because of their demonstrativeness, but in general Frictionless can handle data in Excel, JSON, SQL, and many other formats:

> Download [`country-1.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/main/data/country-1.csv) to reproduce the examples (right-click and "Save link as").

```bash script tabs=CLI
cat country-1.csv
```

```python script tabs=Python
with open('country-1.csv') as file:
    print(file.read())
```

Let's get a Table Schema using the Frictionless framework (note: this example uses YAML for the schema format, but Frictionless also supports JSON format):

```python script tabs=Python
from frictionless import Schema

schema = Schema.describe("country-1.csv")
schema.to_yaml("country.schema.yaml") # use schema.to_json for JSON
```

The high-level functions of Frictionless operate on the dataset and resource levels so we have to use a little bit of Python programming to get the schema information. Below we will show how to use a command-line interface for similar tasks.

```bash script tabs=CLI output=yaml
cat country.schema.yaml
```

```python script tabs=Python output=yaml
with open('country.schema.yaml') as file:
    print(file.read())
```

As we can see, we were able to infer basic metadata from our data file. But describing data doesn't end here - we can provide additional information that we discussed earlier:

> You can edit "country.schema.yaml" manually instead of running Python

```python script tabs=Python
from frictionless import Schema

schema = Schema.describe("country-1.csv")
schema.get_field("id").title = "Identifier"
schema.get_field("neighbor_id").title = "Identifier of the neighbor"
schema.get_field("name").title = "Name of the country"
schema.get_field("population").title = "Population"
schema.get_field("population").description = "According to the year 2020's data"
schema.get_field("population").constraints["minimum"] = 0
schema.foreign_keys.append(
    {"fields": ["neighbor_id"], "reference": {"resource": "", "fields": ["id"]}}
)
schema.to_yaml("country.schema-full.yaml")
```

Let's break it down:
- we added a title for all the fields
- we added a description to the "Population" field; the year information can be critical to interpret the data
- we set a constraint to the "Population" field because it can't be less than 0
- we added a foreign key saying that "Identifier of the neighbor" should be present in the "Identifier" field

```bash script tabs=CLI output=yaml
cat country.schema-full.yaml
```

```python script tabs=Python output=yaml
with open('country.schema-full.yaml') as file:
    print(file.read())
```

Later we're going to show how to use the schema we created to ensure the validity of your data; in the next few sections, we will focus on Data Resource and Data Package metadata.

To continue learning about table schemas please read:
- [Table Schema Spec](https://specs.frictionlessdata.io/table-schema/)
- [API Reference: Schema](../../docs/framework/schema.html#reference-schema)

## Describing a Resource

The Data Resource format describes a data resource such as an individual file or data table.
The essence of a Data Resource is a path to the data file it describes.
A range of other properties can be declared to provide a richer set of metadata including Table Schema for tabular data.

For this section, we will use a file that is slightly more complex to handle. In this example, cells are separated by the ";" character and there is a comment on the top:

> Download [`country-2.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/main/data/country-2.csv) to reproduce the examples (right-click and "Save link as").

```bash script tabs=CLI
cat country-2.csv
```

```python script tabs=Python
with open('country-2.csv') as file:
    print(file.read())
```

Let's describe it:

```bash script tabs=CLI output=yaml
frictionless describe country-2.csv
```

```python script tabs=Python output=yaml
from frictionless import describe

resource = describe('country-2.csv')
print(resource.to_yaml())
```

OK, that looks wrong -- for example, the schema has only inferred one field, and that field does not seem correct either. As we have seen in the "Introductory Guide" Frictionless is capable of inferring some complicated cases' metadata but our data table is too complex for it to automatically infer. We need to manually program it:

> You can edit "country.resource.yaml" manually instead of running Python

```python script tabs=Python
from frictionless import Schema, describe

resource = describe("country-2.csv")
resource.dialect.header_rows = [2]
resource.dialect.get_control('csv').delimiter = ";"
resource.schema = "country.schema.yaml"
resource.to_yaml("country.resource-cleaned.yaml")
```

So what we did here:
- we set the header rows to be row number 2; as humans, we can easily see that was the proper row
- we set the CSV Delimiter to be ";"
- we reuse the schema we created [earlier](#describing-a-schema) as the data has the same structure and meaning

```bash script tabs=CLI output=yaml
cat country.resource-cleaned.yaml
```

```python script tabs=Python output=yaml
with open('country.resource-cleaned.yaml') as file:
    print(file.read())
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
- [API Reference: Resource](../../docs/framework/resource.html#reference-resource)

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

> Download [`country-3.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/main/data/country-3.csv) to reproduce the examples (right-click and "Save link as")

```bash script tabs=CLI
cat country-3.csv
```

```python script tabs=Python
with open('country-3.csv') as file:
    print(file.read())
```

> Download [`capital-3.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/main/data/capital-3.csv) to reproduce the examples (right-click and "Save link as").

```bash script tabs=CLI
cat capital-3.csv
```

```python script tabs=Python
with open('capital-3.csv') as file:
    print(file.read())
```

First of all, let's describe our package now. We did it before for a resource but now we're going to use a glob pattern to indicate that there are multiple files:

```bash script tabs=CLI output=yaml
frictionless describe *-3.csv
```

```python script tabs=Python output=yaml
from frictionless import describe

package = describe("*-3.csv")
print(package.to_yaml())
```

We have already learned about many concepts that are reflected in this metadata. We can see resources, schemas, fields, and other familiar entities. The difference is that this descriptor has information about multiple files which is a popular way of sharing data - in datasets. Very often you have not only one data file but also additional data files, some textual documents e.g. PDF, and others. To package all of these files with the corresponding metadata we use data packages.

Following the pattern that is already familiar to the guide reader, we add some additional metadata:

> You can edit "country.package.yaml" manually instead of running Python

```python script tabs=Python output=yaml
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

```bash script tabs=CLI output=yaml
cat country.package.yaml
```

```python script tabs=Python output=yaml
with open('country.package.yaml') as file:
    print(file.read())
```

The main role of the Data Package descriptor is describing a dataset; as we can see, it includes previously shown descriptors like `schema`, `dialect`, and `resource`. But it would be a mistake to think that Data Package is the least important specification; actually, it completes the Frictionless Data suite making it possible to share and validate not only individual files but also complete datasets.

To continue learning about data resources please read:
- [Data Package Spec](https://specs.frictionlessdata.io/data-package/)
- [API Reference: Package](../../docs/framework/package.html#reference-package)

## Metadata Importance

This documentation contains a great deal of information on how to use metadata and why it's vital for your data. In this section, we're going to provide a quick example based on the "Data Resource" section but please read other documents to get the full picture.

Let's get back to this complex data table:

```bash script tabs=CLI
cat country-2.csv
```

```python script tabs=Python
with open('country-2.csv') as file:
    print(file.read())
```

As we tried before, by default Frictionless can't properly describe this file so we got something like:

```bash script tabs=CLI output=yaml
frictionless describe country-2.csv
```

```python script tabs=Python output=yaml
from frictionless import describe

resource = describe("country-2.csv")
print(resource.to_yaml())
```

Trying to extract the data will fail this way:

```bash script tabs=CLI
frictionless extract country-2.csv
```

```python script tabs=Python output=python
from pprint import pprint
from frictionless import extract

rows = extract("country-2.csv")
pprint(rows)
```

This example highlights a really important idea - without metadata many software will not be able to even read this data file. Furthermore, without metadata people cannot understand the purpose of this data. To see how we can use metadata to fix our data, let's now use the `country.resource-full.yaml` file we created in the "Data Resource" section with Frictionless `extract`:

```bash script tabs=CLI
frictionless extract country.resource-cleaned.yaml
```

```python script tabs=Python
from pprint import pprint
from frictionless import extract

rows = extract("country.resource-cleaned.yaml")
pprint(rows)
```

As we can see, the data is now fixed. The metadata we had saved the day! If we explore this data in Python we can discover that it also corrected data types - e.g. `id` is Python's integer not string. We can now export and share this data without any worries.

## Inferring Metadata

> Many Frictionless Framework's classes are metadata classes as though Schema, Resource, or Package. All the sections below are applicable for all these classes. You can read about the base Metadata class in more detail in [API Reference](../references/api-reference.md#metadata).

Many Frictionless functions infer metadata under the hood such as `describe`, `extract`, and many more. On a lower-level, it's possible to control this process. To see this, let's create a `Resource`.

```python script tabsl=Python output=python
from frictionless import Resource

resource = Resource("country-1.csv")
print(resource)
```
```
{'path': 'country-1.csv'}
```

Frictionless always tries to be as explicit as possible. We didn't provide any metadata except for `path` so we got the expected result. But now, we'd like to `infer` additional metadata:

> We can ask for stats using CLI with `frictionless describe data/table.csv --stats`. Note that we use the `stats` argument for the `resource.infer` function.

```bash script tabs=CLI output=json
frictionless describe country-1.csv --stats --json
```

```python script tabs=Python output=python
from pprint import pprint
from frictionless import Resource

resource = Resource("country-1.csv")
resource.infer(stats=True)
pprint(resource)
```

The result is really familiar to us already. We have seen it a lot as an output of the `describe` function or command. Basically, that's what this high-level function does under the hood: create a resource and then infer additional metadata.

All the main `Metadata` classes have this method with different available options but with the same conceptual purpose:
- `package.infer`
- `resource.infer`

For more advanced detection options, please read the [Detector Guide](framework/detector-guide.md)

## Validating Metadata

Metadata validity is an important topic, and we recommend validating your metadata before publishing. For example, let's first make it invalid:

```python script tabs=Python
import yaml
from frictionless import Resource

descriptor = {}
descriptor['path'] = 'country-1.csv'
descriptor['title'] = 1
try:
    Resource(descriptor)
except Exception as exception:
    print(exception.error)
    print(exception.reasons)
```
```
False
[{'code': 'resource-error', 'name': 'Resource Error', 'tags': [], 'note': '"1 is not of type \'string\'" at "title" in metadata and at "properties/title/type" in profile', 'message': 'The data resource has an error: "1 is not of type \'string\'" at "title" in metadata and at "properties/title/type" in profile', 'description': 'A validation cannot be processed.'}]
```

We see this error`'"1 is not of type \'string\'" at "title" in metadata and at "properties/title/type" in profile'` as we set `title` to be an integer.

Frictionless' high-level functions like `validate` runs all metadata checks by default.

## Transforming Metadata

We have seen this before but let's re-iterate; it's possible to transform core metadata properties using Python's interface:

```python script tabs=Python
from frictionless import Resource

resource = Resource("country.resource-cleaned.yaml")
resource.title = "Countries"
resource.description = "It's a research project"
resource.dialect.header_rows = [2]
resource.dialect.get_control('csv').delimiter = ";"
resource.to_yaml("country.resource-updated.yaml")
```

We can add custom options using the `custom` property:

```python script tabs=Python
from frictionless import Resource

resource = Resource("country.resource-updated.yaml")
resource.custom["customKey1"] = "Value1"
resource.custom["customKey2"] = "Value2"
resource.to_yaml("country.resource-updated2.yaml")
```

Let's check it out:

```bash script tabs=CLI output=yaml
cat country.resource-updated2.yaml
```

```python script tabs=Python output=yaml
with open('country.resource-updated2.yaml') as file:
    print(file.read())
```
