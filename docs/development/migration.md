---
title: Migration
---

Frictionless is a logical continuation of many existing packages created for Frictionless Data as though `datapackage` or `tableschema`. Although, most of these packages will be supported going forward, you can migrate to Frictionless, which is Python 3.6+, as it improves many aspects of working with data and metadata. This document also covers migration from one framework's version to another.

## From v3 to v4

Version 3 of the Frictionless Framework was experimental/unstable and active for 6 months. We improved the framework dramatically during this period of time including various minor API changes and one major API change - `Table` class has been merged into the `Resource` class. Please read the updated documentation to migrate to version 4:
- [Guides Overview](../guides/guides-overview.md)
- [Tutorials Overview](../tutorials/tutorials-overview.md)
- [References Overview](../references/references-overview.md)

## From dataflows

Frictionless Framework provides the `frictionless transform` function for data transformation. It can be used to migrate from `dataflows` or `datapackage-pipelines`:
- [Transform Guide](../guides/transform-guide.md)
- [Transform Steps](../guides/transform-steps.md)

## From goodtables

Frictionless Framework provides the `frictionless validate` function which is in high-level exactly the same as `goodtables validate`. Also `frictionless describe` is an improved version of `goodtables init`. You instead need to use the `frictionless` command instead of the `goodtables` command:
- [Validation Guide](../guides/validation-guide.md)
- [Validation Checks](../guides/validation-checks.md)

## From datapackage

Frictionless Framework has `Package` and `Resource` classes which is almost the same as `datapackage` has:
- [Package Guide](../guides/framework/package-guide.md)
- [Resource Guide](../guides/framework/resource-guide.md)

## From tableschema

Frictionless Framework has `Schema` and `Field` classes which is almost the same as `tableschema` has:
- [Schema Guide](../guides/framework/schema-guide.md)
- [Field Guide](../guides/framework/field-guide.md)

## From tabulator

Frictionless has `Resource` class which is an equivalent of the tabulator's `Stream` class:
- [Resource Guide](../guides/framework/resource-guide.md)
