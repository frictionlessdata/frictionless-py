import boto3
import pytest
import string
import random
from moto import mock_s3
from frictionless import Table


# Loader


@mock_s3
def test_table_s3(bucket_name):

    # Write
    client = boto3.resource("s3", region_name="us-east-1")
    bucket = client.create_bucket(Bucket=bucket_name, ACL="public-read")
    bucket.put_object(
        ACL="private",
        Body=open("data/table.csv", "rb"),
        Bucket=bucket_name,
        ContentType="text/csv",
        Key="table.csv",
    )

    # Read
    with Table("s3://%s/table.csv" % bucket_name) as table:
        assert table.header == ["id", "name"]
        assert table.read_data() == [["1", "english"], ["2", "中国人"]]


# Fixtures


@pytest.fixture
def bucket_name():
    return "bucket_%s" % "".join(random.choice(string.digits) for _ in range(16))
