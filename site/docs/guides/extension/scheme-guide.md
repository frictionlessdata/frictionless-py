---
title: Scheme Guide
---

In Frictionless Framework a scheme is a set of concepts associated with a data source protocol:
- Loader
- Control

The Loader is responsible for loading data from/to different data sources as though local file system or AWS S3. The Control is a simple object to configure the Loader.

## Loader Example

```python script title="Python"
from frictionless import Loader

class S3Loader(Loader):
    remote = True

    # Read

    def read_byte_stream_create(self):
        boto3 = helpers.import_from_plugin("boto3", plugin="s3")
        control = self.resource.control
        parts = urlparse(self.resource.fullpath, allow_fragments=False)
        client = boto3.resource("s3", endpoint_url=control.endpoint_url)
        object = client.Object(bucket_name=parts.netloc, key=parts.path[1:])
        byte_stream = S3ByteStream(object)
        return byte_stream

    # Write

    def write_byte_stream_save(self, byte_stream):
        boto3 = helpers.import_from_plugin("boto3", plugin="s3")
        control = self.resource.control
        parts = urlparse(self.resource.fullpath, allow_fragments=False)
        client = boto3.resource("s3", endpoint_url=control.endpoint_url)
        object = client.Object(bucket_name=parts.netloc, key=parts.path[1:])
        object.put(Body=byte_stream)
```

## Control Example

```python script title="Python"
from frictionless import Control

class S3Control(Control):

    def __init__(self, descriptor=None, endpoint_url=None):
        self.setinitial("endpointUrl", endpoint_url)
        super().__init__(descriptor)

    @property
    def endpoint_url(self):
        return (
            self.get("endpointUrl")
            or os.environ.get("S3_ENDPOINT_URL")
            or DEFAULT_ENDPOINT_URL
        )

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("endpointUrl", self.endpoint_url)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "endpointUrl": {"type": "string"},
        },
    }
```

## References

- [Loader](../../references/api-reference.md#loader)
- [Control](../../references/api-reference.md#control)
