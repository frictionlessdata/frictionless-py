import pytest
from frictionless import Resource, Pipeline, steps, resources


# General


@pytest.mark.skip
def test_step_table_write(tmpdir):
    path = str(tmpdir.join("table.json"))

    # Write
    source = Resource("data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.cell_set(field_name="population", value=100),
            steps.table_write(path=path),
        ],
    )
    source.transform(pipeline)

    # Read
    resource = resources.TableResource(path=path)
    assert resource.read_rows() == [
        {"id": 1, "name": "germany", "population": 100},
        {"id": 2, "name": "france", "population": 100},
        {"id": 3, "name": "spain", "population": 100},
    ]
