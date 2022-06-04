import pytest
from frictionless import Resource, FrictionlessException, steps


# General


def test_step_table_validate():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.cell_set(field_name="population", value="bad"),
            steps.table_validate(),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    with pytest.raises(FrictionlessException) as excinfo:
        target.read_rows()
    error = excinfo.value.error
    assert error.code == "step-error"
    assert error.note.count('type is "integer/default"')
