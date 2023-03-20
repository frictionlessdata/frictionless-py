# Convert

```markdown remark type=warning
This command currenlty is in active development and for dialect updated there are very few options available
```

```markdown remark type=info
Wit this command Frictionless will drop all invalid data like type errors in cells. Use `validate` if needed.
```

With `convert` command you can quickly convert a tabular data file from one format to another (or the same format with different dialect):

## Format Conversion

For example, let's convert a CSV file into an Excel:

```bash tabs=CLI
frictionless convert table.csv table.xlsx
```

## Downloading Files

The command can be used for downloading files as well. For example, let's cherry-pick one CSV file from a Zenodo dataset:

```bash tabs=CLI
frictionless convert https://zenodo.org/record/3977957 --name aaawrestlers --to-path test.csv
```

## Dialect Updates

Consider, we want to change the CSV delimiter:

```bash tabs=CLI
frictionless convert table.csv table-copy.csv --csv-delimiter ;
```
