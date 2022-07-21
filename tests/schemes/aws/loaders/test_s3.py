import boto3
import pytest
import string
import random
from moto import mock_s3
from frictionless import Package, Resource, Dialect, platform


# Read


@mock_s3
def test_s3_loader(bucket_name):

    # Write
    client = boto3.resource("s3", region_name="us-east-1")
    bucket = client.create_bucket(Bucket=bucket_name, ACL="public-read")  # type: ignore
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


# Write


@mock_s3
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_s3_loader_write(bucket_name):
    client = boto3.resource("s3", region_name="us-east-1")
    client.create_bucket(Bucket=bucket_name, ACL="public-read")  # type: ignore

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


@mock_s3
@pytest.mark.ci
@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_s3_loader_big_file(bucket_name):

    # Write
    client = boto3.resource("s3", region_name="us-east-1")
    bucket = client.create_bucket(Bucket=bucket_name, ACL="public-read")  # type: ignore
    bucket.put_object(
        ACL="private",
        Body=open("data/table-1MB.csv", "rb"),
        Bucket=bucket_name,
        ContentType="text/csv",
        Key="table1.csv",
    )

    # Read
    dialect = Dialect(header=False)
    with Resource("s3://%s/table1.csv" % bucket_name, dialect=dialect) as resource:
        assert resource.read_rows()
        assert resource.stats.to_descriptor() == {
            "md5": "78ea269458be04a0e02816c56fc684ef",
            "sha256": "aced987247a03e01acde64aa6b40980350b785e3aedc417ff2e09bbeacbfbf2b",
            "bytes": 1000000,
            "fields": 10,
            "rows": 10000,
        }


# Bugs


@mock_s3
def test_s3_loader_multiprocessing_problem_issue_496(bucket_name):

    # Write
    client = boto3.resource("s3", region_name="us-east-1")
    bucket = client.create_bucket(Bucket=bucket_name, ACL="public-read")  # type: ignore
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
    package = Package(descriptor)
    print(package.to_descriptor())
    report = package.validate()
    assert report.valid
    assert report.stats.tasks == 2


@mock_s3
def test_s3_loader_problem_with_spaces_issue_501(bucket_name):

    # Write
    client = boto3.resource("s3", region_name="us-east-1")
    bucket = client.create_bucket(Bucket=bucket_name, ACL="public-read")  # type: ignore
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


# Fixtures


@pytest.fixture
def bucket_name():
    return "bucket_%s" % "".join(random.choice(string.digits) for _ in range(16))
