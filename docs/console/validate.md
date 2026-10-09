---
script:
  basepath: data
---

# Validate

```markdown remark type=warning
For more information for data validation with Frictionless, read this [Validating Data](../guides/validating-data.html) tutorial.
```

With `validate` command you can validate your tabular files (individual or the whole dataset). For example:

```bash script tabs=CLI
frictionless validate table.csv invalid.csv
```

## Descriptor filenames and validation types

Type inference considers recognized filename endings before inspecting descriptor
contents. For example, `schema.json` and `schema.yaml` select schema metadata
validation. Renaming a resource descriptor to one of those names does not turn
it into a schema, and validation may report a schema error instead of checking
the referenced data.

`describe --json` on a CSV produces a resource descriptor, which includes the
data path and a nested schema. Save it as `resource.json` when you want to
validate the referenced data:

```bash
frictionless describe --json data.csv > resource.json
frictionless validate resource.json
```

If the resource descriptor is already named `schema.json`, override inference:

```bash
frictionless validate schema.json --type resource
```

The `--type` option selects how the source is interpreted. It differs from
`--schema`, which supplies a table schema for validating data; a complete
resource descriptor is not a table schema. Validating schema metadata alone
does not validate the rows in a CSV file.
