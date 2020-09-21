import os
import io
import requests.utils
from urllib.parse import urlparse
from ..controls import Control
from ..plugin import Plugin
from ..loader import Loader
from .. import helpers


# Plugin


class AwsPlugin(Plugin):
    """Plugin for AWS

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.aws import AwsPlugin`

    """

    def create_control(self, file, *, descriptor):
        if file.scheme == "s3":
            return S3Control(descriptor)

    def create_loader(self, file):
        if file.scheme == "s3":
            return S3Loader(file)


# Control


class S3Control(Control):
    """S3 control representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.aws import S3Control`

    Parameters:
        descriptor? (str|dict): descriptor
        endpoint_url? (string): endpoint url

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, endpoint_url=None, detect_encoding=None):
        self.setinitial("endpointUrl", endpoint_url)
        super().__init__(descriptor, detect_encoding=detect_encoding)

    @property
    def endpoint_url(self):
        super().expand()
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
        "properties": {"endpointUrl": {"type": "string"}, "detectEncoding": {}},
    }


# Loader


class S3Loader(Loader):
    """S3 loader implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.aws import S3Loader`

    """

    remote = True

    # Read

    def read_byte_stream_create(self):
        boto3 = helpers.import_from_plugin("boto3", plugin="aws")
        control = self.file.control
        client = boto3.client("s3", endpoint_url=control.endpoint_url)
        source = requests.utils.requote_uri(self.file.source)
        parts = urlparse(source, allow_fragments=False)
        response = client.get_object(Bucket=parts.netloc, Key=parts.path[1:])
        # https://github.com/frictionlessdata/tabulator-py/issues/271
        byte_stream = io.BufferedRandom(io.BytesIO())
        byte_stream.write(response["Body"].read())
        byte_stream.seek(0)
        return byte_stream


# Internal

DEFAULT_ENDPOINT_URL = "https://s3.amazonaws.com"
