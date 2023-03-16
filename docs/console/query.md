# Query

```markdown remark type=info
Wit this command Frictionless will drop all invalid data like type errors in cells. Use `validate` if needed.
```

With `query` command you can explore tabular files within a Sqlite database.

## Installation

```bash tabs=CLI
pip install frictionless[sql]
pip install frictionless[sql,zenodo] # for examples in this tutorial
```

## Usage

```bash
frictionless query https://zenodo.org/record/3977957
```

```yaml image
path: ../../assets/query.png
width: unset
height: unset
```
