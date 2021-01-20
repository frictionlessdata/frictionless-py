---
title: S3 Tutorial
sidebar_label: S3
---

:::caution
This functionality requires an experimental `s3` plugin. [Read More](../references/plugins-reference.md)
:::

Frictionless supports reading data from S3 cloud source. You can read file in any format that is available in your bucket.

```bash
! pip install frictionless[s3]
```


## Reading from S3

You can read from this source using `Package/Resource` or `Table` API, for example:

```python
from frictionless import Resource

resource = Resource(path='s3://bucket/table.csv')
print(resource.read_rows())
```


For reading from a private bucket you need to setup AWS creadentials as it's described in [Boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables).

## Writing to S3

The same is actual for writing:

```python
from frictionless import Resource

resource = Resource(path='data/table.csv')
resource.write('s3://bucket/table.csv')
```


## Configuring S3

There is a control to configure how Frictionless read files in this storage. For example:

```python
from frictionless import Resource
from frictionless.plugins.s3 import S3Control

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table.new.csv', control=controls.S3Control(endpoint_url='<url>'))
```


References:
- [S3 Control](https://frictionlessdata.io/tooling/python/schemes-reference/#s3)
