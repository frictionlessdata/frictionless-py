---
title: S3 Tutorial
sidebar_label: S3
---

> This functionality requires an experimental `s3` plugin. [Read More](../../references/plugins-reference.md)

Frictionless supports reading data from an S3 cloud source. You can read files in any format that is available in your bucket.

```bash title="CLI"
pip install frictionless[s3]
```

## Reading Data

You can read from this source using `Package/Resource`, for example:

```python title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource(path='s3://bucket/table.csv')
pprint(resource.read_rows())
```

For reading from a private bucket you need to setup AWS creadentials as it's described in the [Boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables).

## Writing Data

The same can be done for writing:

```python title="Python"
from frictionless import Resource

resource = Resource(path='data/table.csv')
resource.write('s3://bucket/table.csv')
```

## Configuring Data

There is a `Control` to configure how Frictionless read files in this storage. For example:

```python title="Python"
from frictionless import Resource
from frictionless.plugins.s3 import S3Control

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table.new.csv', control=controls.S3Control(endpoint_url='<url>'))
```

References:
- [S3 Control](../../references/schemes-reference.md#s3)
