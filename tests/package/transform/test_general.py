import pytest
from frictionless import Package, Pipeline, steps


# General


@pytest.mark.skip(reason="issue-1221")
def test_transform_package():
    source = Package("data/tables/chunk*.csv")
    pipeline = Pipeline(
        steps=[
            steps.resource_transform(
                name="chunk1",
                steps=[
                    steps.table_merge(resource="chunk2"),
                ],
            ),
            steps.resource_remove(name="chunk2"),
        ],
    )
    target = source.transform(pipeline)
    assert target.resource_names == ["chunk1"]
    assert target.get_resource("chunk1").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_pipeline_package():
    source = Package("data/package/datapackage.json")
    pipeline = Pipeline.from_descriptor(
        {
            "steps": [
                {"type": "resource-remove", "name": "data2"},
            ],
        }
    )
    target = source.transform(pipeline)
    assert target.resource_names == ["data"]
