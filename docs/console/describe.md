---
script:
  basepath: data
---

# Describe

```markdown remark type=info
The difference with between `describe` and `list` command: if `datapackage.json` is not provided `describe` will load a sample from every tabular data file in a dataset and infer a schema while `list` is a very lean and quick command operating only with available metadata and not touching actual data files.
```

With Frtictionless `describe` command you can get a metadata of file or a dataset.

## Normal Mode

By default, it outputs metadata visually formatted:

```bash script tabs=CLI
frictionless describe tables/*.csv
```

## Yaml/Json Mode

It's possible to output as `YAML` or `JSON`, for example:

```bash script tabs=CLI
frictionless describe tables/*.csv --yaml
```
