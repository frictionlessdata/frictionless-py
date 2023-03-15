---
script:
  basepath: data
---

# Extract

With Frtictionless `extract` command you can extract data from a file or a dataset.

## Normal Mode

By default, it outputs metadata visually formatted:

```bash script tabs=CLI
frictionless extract tables/*.csv
```

## Yaml/Json Mode

It's possible to output as `YAML` or `JSON`, for example:

```bash script tabs=CLI
frictionless extract tables/*.csv --yaml
```
