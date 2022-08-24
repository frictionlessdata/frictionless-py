---
title: FAQ
---

## Can I use Frictionless Data with tabular data in Pandas dataframes?

Yes. Please read the [Pandas Tutorial](tutorials/formats/pandas-tutorial.md).

## Why am I getting the error: "cannot extract tabular data from JSON"?

Please update your `frictionless` version. Nowadays, Frictionless treats all JSON and YAML files as metadata by default so this error should not present.

## Is there a way to specify that the same fields should be expected across multiple files?

Yes, you just need to create a Table Schema and re-use it (the same can be done for a Dialect):

```bash title="CLI"
frictionless describe reference.csv --type dialect > dialect.yaml
frictionless describe reference.csv --type schema > schema.yaml
frictionless validate table.csv --dialect dialect.yaml --schema schema.yaml
```

If you work with a data package you can have `package.resources[].schema = "path/to/schema.json"` although it's not possible to share a subset of fields only the whole schema. For sharing a subset of fields you need to copy them.

## Is it possible to write in the schema that the name of the column is optional?

Yes, your resource can have `resource.layout.header = False` in Python.

## Can I handle a two-line header with Frictionless Data?

Yes, you need to use `resource.layout.header_rows = [1,2,3]` in Python or `--header-rows 1,2,3` in CLI. Also, Here is an example of a [More Complex Use Case](https://replit.com/@rollninja/Frictionless-meta-in-the-2nd-row#main.py).

## What is the relationship between a Frictionless JSON file and something that's indexed by e.g. Google Datasets? Are they compatible?

The main difference is that Google datasets search use schema.org, which supports JSON-LD. We currently don't support linked data like JSON-LD. But they are compatible. Something like DataCite is more specific than Frictionless. Frictionless is general by design, and can be expanded to be compatible with other schemas and standards.

## Is there a way to directly infer/describe SQLite/Pandas/Parquet files?

> Currently, Parquet data is not supported but it's on our roadmap.

Yes, please follow the [Describe Guide](guides/describing-data.md) but instead of local CSV path provide a SQLite url or Pandas dataframe object. For more information about individual data formats please take a look at [Formats Tutorials](tutorials/formats/sql-tutorial.md).

## What is the relationship between JSON Schema and the Frictionless Data json format?

We use JSON Schema to validate our metadata. JSON Schema (we call it profile) is a sort of meta-meta-data for us. We validate our metadata using JSON Schema (profiles).

If you use JSON Schema to describe your tabular data, you can use `Schema.from_jsonschema` helper function to translate it to Table Schema.

## Can I use Frictionless with complex nested objects?

Frictionless works with data sources that have tabular structure. Individual files in Frictionless can be `objects` or `arrays` so you can maintain nested data using these data types. On the other hand, you might need to use other tools like JSON Schema if structure of your data is to complex.

## Can I validate a package with primary/foreign key relations?

Yes, you can use `package.resources[].schema.foreign_keys` in Python [to add foreign keys to your schema](guides/describing-data/#describing-a-schema), and when you validate your data. If there are integrity errors, you will get a [Foreign Key Error](references/errors-reference/#foreignkey-error).

## Can I add a custom attribute (e.g. to indicate the datetime a package was updated)?

If the spec doesn't have (yet) this attribute, you can add it. For an examaple, please take a look at [Describe Guide](guides/describing-data/#transforming-metadata)

## Is it possible to validate a single resource from a datapackage.json?

> We're planning to add this functionality to the CLI as well.

It's possible using Python:

```python title="Python"
from frictionless import Package, validate

package = Package('datapackage.json')
resource = package.get_resource('name')
report = validate(resource)
```

## Why am I getting the error: “zsh: no matches found: frictionless[sql]” after pip install frictionless[sql]?

If you're using zsh linux terminal instead of bash, is good to know that zsh [uses square brackets for globbing / pattern matching](http://zsh.sourceforge.net/Guide/zshguide05.html#l137)

That means that if you need to pass literal square brackets as an argument to a command, you either need to escape them or quote the argument like this:

```
pip install 'requests[security]'
```
So, I this case:

```
pip install 'frictionless[sql]'
```

[Stackoverflow reference](https://stackoverflow.com/questions/30539798/zsh-no-matches-found-requestssecurity)
