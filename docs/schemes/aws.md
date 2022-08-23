# AWS Schemes

Frictionless supports reading data from a AWS cloud source. You can read files in any format that is available in your S3 bucket.

```bash tabs=CLI
pip install frictionless[aws]
pip install 'frictionless[aws]' # for zsh shell
```

## Reading Data

You can read from this source using `Package/Resource`, for example:

```python tabs=Python
from pprint import pprint
from frictionless import Resource

resource = Resource(path='s3://bucket/table.csv')
pprint(resource.read_rows())
```

For reading from a private bucket you need to setup AWS creadentials as it's described in the [Boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables).

## Writing Data

A similiar approach can be used for writing:

```python tabs=Python
from frictionless import Resource

resource = Resource(path='data/table.csv')
resource.write('s3://bucket/table.csv')
```

## Configuration

There is a `Control` to configure how Frictionless read files in this storage. For example:

```python tabs=Python
from frictionless import Resource
from frictionless.plugins.s3 import S3Control

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table.new.csv', control=controls.S3Control(endpoint_url='<url>'))
```

## Reference

```yaml reference
references:
  - frictionless.schemes.AwsControl
```
