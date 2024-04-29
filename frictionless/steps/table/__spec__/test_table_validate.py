import pytest

from frictionless import FrictionlessException, Pipeline, steps
from frictionless.resources import TableResource

# General


def test_step_table_validate():
    source = TableResource(path="data/transform.csv")
    pipeline = Pipeline(
        steps=[
            steps.cell_set(field_name="population", value="bad"),
            steps.table_validate(),
        ],
    )
    target = source.transform(pipeline)
    assert target.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    with pytest.raises(FrictionlessException) as excinfo:
        target.read_rows()
    error = excinfo.value.error
    assert error.type == "step-error"
    assert error.note.count('type is "integer/default"')
