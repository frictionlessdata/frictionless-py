---
script:
  basepath: data
---

# Index

```markdown remark type=info
Wit this command Frictionless will drop all invalid data like type errors in cells. Use `validate` if needed.
```

```markdown remark type=warning
This functionality has been published in `frictionless@5.5` as a feature preview and request for comments. The implementation is raw and doesn't cover many edge cases.
```

Indexing resource in Frictionless terms means loading a data table into a database. Let's explore how this feature works in different modes.

## Installation

```bash tabs=CLI
pip install frictionless[sql]
```

## Normal Mode

This mode is supported for any database that is supported by `sqlalchemy`. Under the hood, Frictionless will infer Table Schema and populate the data table as it normally reads data. It means that type errors will be replaced by `null` values and in-general it guarantees to finish successfully for any data even very invalid.

```bash script tabs=CLI
frictionless index table.csv --database sqlite:///index/project.db
frictionless extract sqlite:///index/project.db --table table --json
```

## Fast Mode

```markdown remark type=warning
For the SQLite in fast mode, it requires `sqlite3@3.34+` command to be available.
```

Fast mode is supported for SQLite and Postgresql databases. It will infer Table Schema using a data sample and index data using `COPY` in Potgresql and `.import` in SQLite. For big data files this mode will be 10-30x faster than normal indexing but the speed comes with the price -- if there is invalid data the indexing will fail.

```bash script tabs=CLI
frictionless index table.csv --database sqlite:///index/project.db --fast
frictionless extract sqlite:///index/project.db --table table --json
```

### Solution 1: Fallback

To ensure that the data will be successfully indexed it's possible to use `fallback` option. If the fast indexing fails Frictionless will start over in normal mode and finish the process successfully.

```bash tabs=CLI
frictionless index table.csv --database sqlite:///index/project.db --name table --fast --fallback
```

### Solution 2: QSV

Another option is to provide a path to [QSV](https://github.com/jqnatividad/qsv) binary. In this case, initial schema inferring will be done based on the whole data file and will guarantee that the table is valid type-wise:

```bash tabs=CLI
frictionless index table.csv --database sqlite:///index/project.db --name table --fast --qsv qsv_path
```
