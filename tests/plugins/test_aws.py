import boto3
import pytest
import string
import random
from moto import mock_s3
from frictionless import Table, validate


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


@mock_s3
def test_table_s3_big_file(bucket_name):

    # Write
    client = boto3.resource("s3", region_name="us-east-1")
    bucket = client.create_bucket(Bucket=bucket_name, ACL="public-read")
    bucket.put_object(
        ACL="private",
        Body=open("data/table1.csv", "rb"),
        Bucket=bucket_name,
        ContentType="text/csv",
        Key="table1.csv",
    )

    # Read
    with Table("s3://%s/table1.csv" % bucket_name) as table:
        assert table.read_rows()
        assert table.stats == {
            "hash": "78ea269458be04a0e02816c56fc684ef",
            "bytes": 1000000,
            "fields": 10,
            "rows": 10000,
        }


@mock_s3
@pytest.mark.ci
def test_s3_validate_multiprocessing_problem_issue_496(bucket_name):

    # Write
    client = boto3.resource("s3", region_name="us-east-1")
    bucket = client.create_bucket(Bucket=bucket_name, ACL="public-read")
    bucket.put_object(
        ACL="private",
        Body=open("data/table.csv", "rb"),
        Bucket=bucket_name,
        ContentType="text/csv",
        Key="table1.csv",
    )
    bucket.put_object(
        ACL="private",
        Body=open("data/table.csv", "rb"),
        Bucket=bucket_name,
        ContentType="text/csv",
        Key="table2.csv",
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
    assert report.stats["tables"] == 2


# Fixtures


@pytest.fixture
def bucket_name():
    return "bucket_%s" % "".join(random.choice(string.digits) for _ in range(16))
