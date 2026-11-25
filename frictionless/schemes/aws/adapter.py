from __future__ import annotations

import io
import json
from typing import Any, Optional
from urllib.parse import urlparse

from ... import helpers
from ...exception import FrictionlessException
from ...package import Package
from ...platform import platform
from ...system import Adapter
from .control import AwsControl


class AwsAdapter(Adapter):
    def __init__(self, source: Any, *, basepath: Optional[str] = None):
        self.source = source
        self.basepath = basepath

    # Read

    def read_package(self):
        normsource = helpers.join_basepath(self.source, basepath=self.basepath)
        parts = urlparse(normsource, allow_fragments=False)
        if parts.scheme == "s3":
            control = AwsControl()
            client = platform.boto3.resource("s3", endpoint_url=control.s3_endpoint_url)
            object = client.Object(bucket_name=parts.netloc, key=parts.path[1:])
            try:
                content = object.get()["Body"].read().decode()
            except client.meta.client.exceptions.NoSuchBucket:
                note = f'No such bucket: "{parts.netloc}"'
                raise FrictionlessException(note)
            except client.meta.client.exceptions.NoSuchKey:
                note = f'No such key: "{parts.path}"'
                raise FrictionlessException(note)
            except client.meta.client.exceptions.ClientError as exception:
                note = f'AWS error: "{exception}"'
                raise FrictionlessException(note)
            except Exception as exception:
                note = f'Cannot read package: "{exception}"'
                raise FrictionlessException(note) from exception
            else:
                if normsource.endswith(".yaml"):
                    descriptor = platform.yaml.safe_load(io.StringIO(content))
                else:
                    descriptor = json.loads(content)

                basepath = normsource.rsplit("/", 1)[0]
                return Package.from_descriptor(descriptor, basepath=basepath)

        note = "Cannot read package"
        raise FrictionlessException(note)
