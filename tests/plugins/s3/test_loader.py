import boto3
import pytest
import string
import random
from moto import mock_s3
from frictionless import Resource, Layout, validate, helpers


IS_UNIX = not helpers.is_platform("windows")


# General


@mock_s3
def test_s3_loader(bucket_name):
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
    with Resource("s3://%s/table.csv" % bucket_name) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@mock_s3
@pytest.mark.ci
def test_s3_loader_big_file(bucket_name):
    # Write
    client = boto3.resource("s3", region_name="us-east-1")
    bucket = client.create_bucket(Bucket=bucket_name, ACL="public-read")
    bucket.put_object(
        ACL="private",
        Body=open("data/table-1MB.csv", "rb"),
        Bucket=bucket_name,
        ContentType="text/csv",
        Key="table1.csv",
    )

    # Read
    layout = Layout(header=False)
    with Resource("s3://%s/table1.csv" % bucket_name, layout=layout) as resource:
        assert resource.read_rows()
        if IS_UNIX:
            assert resource.stats == {
                "hash": "78ea269458be04a0e02816c56fc684ef",
                "bytes": 1000000,
                "fields": 10,
                "rows": 10000,
            }


@mock_s3
def test_s3_loader_multiprocessing_problem_issue_496(bucket_name):
    # Write
    client = boto3.resource("s3", region_name="us-east-1")
    bucket = client.create_bucket(Bucket=bucket_name, ACL="public-read")
    for number in [1, 2]:
        bucket.put_object(
            ACL="private",
            Body=open("data/table.csv", "rb"),
            Bucket=bucket_name,
            ContentType="text/csv",
            Key=f"table{number}.csv",
        )

    # Validate
    descriptor = {
        "resources": [
            {"path": "s3://%s/table1.csv" % bucket_name},
            {"path": "s3://%s/table2.csv" % bucket_name},
        ]
    }
    report = validate(descriptor)
    assert report.valid
    assert report.stats["tasks"] == 2


@mock_s3
def test_s3_loader_problem_with_spaces_issue_501(bucket_name):
    # Write
    client = boto3.resource("s3", region_name="us-east-1")
    bucket = client.create_bucket(Bucket=bucket_name, ACL="public-read")
    bucket.put_object(
        ACL="private",
        Body=open("data/table.csv", "rb"),
        Bucket=bucket_name,
        ContentType="text/csv",
        Key="table with space.csv",
    )

    # Read
    with Resource("s3://%s/table with space.csv" % bucket_name) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


@mock_s3
def test_s3_loader_write(bucket_name):
    client = boto3.resource("s3", region_name="us-east-1")
    client.create_bucket(Bucket=bucket_name, ACL="public-read")

    # Write
    with Resource("data/table.csv") as resource:
        resource.write(Resource("s3://%s/table.csv" % bucket_name))

    # Read
    with Resource("s3://%s/table.csv" % bucket_name) as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


# Fixtures


@pytest.fixture
def bucket_name():
    return "bucket_%s" % "".join(random.choice(string.digits) for _ in range(16))
