import pytest

from frictionless import Pipeline, steps
from frictionless.resources import TableResource

# General


@pytest.mark.skip
def test_step_table_write(tmpdir):
    path = str(tmpdir.join("table.json"))

    # Write
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.cell_set(field_name="population", value=100),
            steps.table_write(path=path),
        ],
    )
    source.transform(pipeline)

    # Read
    resource = TableResource(path=path)
    assert resource.read_rows() == [
        {"id": 1, "name": "germany", "population": 100},
        {"id": 2, "name": "france", "population": 100},
        {"id": 3, "name": "spain", "population": 100},
    ]
