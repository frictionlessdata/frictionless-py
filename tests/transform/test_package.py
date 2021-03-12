from frictionless import transform, describe, steps


# General


def test_transform_package():
    source = describe("data/tables/chunk*.csv")
    target = transform(
        source,
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
    assert target.resource_names == ["chunk1"]
    assert target.get_resource("chunk1").read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]
