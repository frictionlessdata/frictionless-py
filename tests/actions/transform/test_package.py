import pytest
from frictionless import Package, transform, steps


# General


@pytest.mark.skip(reason="issue-1221")
def test_transform_package():
    target = transform(
        "data/tables/chunk*.csv",
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
    assert isinstance(target, Package)
    assert target.resource_names == ["chunk1"]
    assert target.get_resource("chunk1").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
