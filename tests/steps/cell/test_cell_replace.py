from frictionless import Resource, steps


# General


def test_step_cell_replace():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.cell_replace(pattern="france", replace="FRANCE"),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "FRANCE", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_cell_replace_with_field_name():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.cell_replace(pattern="france", replace="FRANCE", field_name="id"),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_cell_replace_using_regex():
    source = Resource(path="data/transform.csv")
    target = source.transform(
        steps=[
            steps.cell_replace(
                pattern="<regex>.*r.*", replace="center", field_name="name"
            ),
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
        ]
    }
    assert target.read_rows() == [
        {"id": 1, "name": "center", "population": 83},
        {"id": 2, "name": "center", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]
