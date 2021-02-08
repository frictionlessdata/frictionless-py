import pytest
from frictionless import Resource, transform, steps


# General


@pytest.mark.skip
def test_transform():
    source = Resource(path="data/transform.csv")
    source.infer()
    target = transform(
        source,
        steps=[
            steps.table_normalize(),
            steps.table_melt(field_name="id"),
            steps.table_recast(field_name="id"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_transform_custom_step_function_based():

    # Create step
    def custom(resource):
        with resource:
            for row in resource.row_stream:
                row["id"] = row["id"] * row["id"]
                yield row

    # Transform resource
    source = Resource(path="data/transform.csv")
    source.infer()
    target = transform(source, steps=[custom])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 4, "name": "france", "population": 66},
        {"id": 9, "name": "spain", "population": 47},
    ]
