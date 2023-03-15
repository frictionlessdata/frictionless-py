# Convert

```markdown remark type=warning
This command currenlty is in active development and for dialect updated there are very few options available
```

With `convert` command you can quickly convert a tabular data file from one format to another (or the same format with different dialect):

## Format Conversion

For example, let's convert a CSV file into an Excel:

```bash tabs=CLI
frictionless convert table.csv table.xlsx
```

## Dialect Updates

Consider, we want to change the CSV delimiter:

```bash tabs=CLI
frictionless convert table.csv table-copy.csv --csv-delimiter ;
```
