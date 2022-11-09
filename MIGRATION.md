# Migration

Frictionless is a logical continuation of many existing packages created for Frictionless Data as though `datapackage` or `tableschema`. Although, most of these packages will be supported going forward, you can migrate to Frictionless, which is Python 3.8+, as it improves many aspects of working with data and metadata. This document also covers migration from one framework's version to another.

## From v4 to v5

Since the initial Frictionless Framework release we'd been collecting feedback and analyzing both high-level users' needs and bug reports to identify shortcomings and areas that can be improved in the next version of the framework. Read about a new version of the framework and migration details in this blog:

- [Welcome Frictionless Framework (v5)](../../blog/2022/08-22-frictionless-framework-v5.html)

## From dataflows

Frictionless Framework provides the `frictionless transform` function for data transformation. It can be used to migrate from `dataflows` or `datapackage-pipelines`:
- [Transforming Data](../guides/transforming-data.html)
- [Transform Steps](../steps/resource.html)

## From goodtables

Frictionless Framework provides the `frictionless validate` function which is in high-level exactly the same as `goodtables validate`. Also `frictionless describe` is an improved version of `goodtables init`. You instead need to use the `frictionless` command instead of the `goodtables` command:
- [Validating Data](../guides/validating-data.html)
- [Validation Checks](../checks/baseline.html)
- [Validation Errors](../errors/metadata.html)

## From datapackage

Frictionless Framework has `Package` and `Resource` classes which is almost the same as `datapackage` has:

- [Describing Data](../guides/describing-data.html)
- [Extracting Data](../guides/extracting-data.html)
- [Package Class](../framework/package.html)
- [Resource Class](../framework/resource.html)

## From tableschema

Frictionless Framework has `Schema` and `Field` classes which is almost the same as `tableschema` has:

- [Describing Data](../guides/describing-data.html)
- [Extracting Data](../guides/extracting-data.html)
- [Schema Class](../framework/schema.html)
- [Tabular Fields](../fields/any.html)

## From tabulator

Frictionless has `Resource` class which is an equivalent of the tabulator's `Stream` class:

- [Extracting Data](../guides/extracting-data.html)
- [Resource Class](../framework/resource.html)
- [File Schemes](../schemes/aws.html)
- [File Formats](../formats/csv.html)
