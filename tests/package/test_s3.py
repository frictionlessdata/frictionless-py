import random
import string

import boto3
import pytest
from moto import mock_s3

from frictionless import Package

# Read


@mock_s3
def test_s3_package(bucket_name):
    # Write
    client = boto3.resource("s3", region_name="us-east-1")
    bucket = client.create_bucket(Bucket=bucket_name, ACL="public-read")  # type: ignore
    bucket.put_object(
        ACL="private",
        Body=open("data/package.json", "rb"),
        Bucket=bucket_name,
        ContentType="text/json",
        Key="package.json",
    )

    # Read
    package = Package(f"s3://{bucket_name}/package.json")

    assert package.name == "name"
    assert package.basepath == f"s3://{bucket_name}"
    assert package.to_descriptor() == {
        "name": "name",
        "resources": [
            {
                "name": "name",
                "type": "table",
                "path": "table.csv",
                "scheme": "file",
                "format": "csv",
                "mediatype": "text/csv",
            },
        ],
    }


# Fixtures


@pytest.fixture
def bucket_name():
    return "bucket_%s" % "".join(random.choice(string.digits) for _ in range(16))
