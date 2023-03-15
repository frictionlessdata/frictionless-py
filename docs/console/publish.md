# Publish

```markdown remark type=warning
Currently, only publishing to CKAN is supported; Github and Zenodo are in active development.
```

With `publish` command you can publish your dataset to a data publishing platform like CKAN:

```bash
frictionless publish data/tables/*.csv --target http://ckan:5000/dataset/my-best --title "My best dataset"
```

It will ask for an API Key to upload your metadata and data. As a result:

```yaml image
path: ../../assets/publish.png
width: unset
height: unset
```
