from frictionless import Resource, transform, steps


# Replace Cells


def test_step_replace_cells():
    source = Resource(path="data/transform.csv")
    target = transform(
        source, steps=[steps.replace_cells(source="france", target="FRANCE")]
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "FRANCE", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_replace_cells_with_name():
    source = Resource(path="data/transform.csv")
    target = transform(
        source, steps=[steps.replace_cells(source="france", target="FRANCE", name="id")]
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


# Fill Cells


def test_step_fill_cells():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.replace_cells(source="france", target=None),
            steps.fill_cells(name="name", value="FRANCE"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "FRANCE", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_fill_cells_direction_down():
    source = Resource(path="data/transform.csv")
    target = transform(
        source,
        steps=[
            steps.replace_cells(source="france", target=None),
            steps.fill_cells(direction="down"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "germany", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_fill_cells_direction_right():
    source = Resource(path="data/transform.csv")
    source.infer(only_sample=True)
    source.schema.get_field("id").type = "string"
    source.schema.get_field("population").type = "string"
    target = transform(
        source,
        steps=[
            steps.replace_cells(source="france", target=None),
            steps.fill_cells(direction="right"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": "1", "name": "germany", "population": "83"},
        {"id": "2", "name": "2", "population": "66"},
        {"id": "3", "name": "spain", "population": "47"},
    ]


def test_step_fill_cells_direction_left():
    source = Resource(path="data/transform.csv")
    source.infer(only_sample=True)
    source.schema.get_field("id").type = "string"
    source.schema.get_field("population").type = "string"
    target = transform(
        source,
        steps=[
            steps.replace_cells(source="france", target=None),
            steps.fill_cells(direction="left"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": "1", "name": "germany", "population": "83"},
        {"id": "2", "name": "66", "population": "66"},
        {"id": "3", "name": "spain", "population": "47"},
    ]


# Convert Cells


def test_step_convert_cells():
    source = Resource(path="data/transform.csv")
    source.infer(only_sample=True)
    source.schema.get_field("id").type = "string"
    source.schema.get_field("population").type = "string"
    target = transform(source, steps=[steps.convert_cells(value="n/a")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": "n/a", "name": "n/a", "population": "n/a"},
        {"id": "n/a", "name": "n/a", "population": "n/a"},
        {"id": "n/a", "name": "n/a", "population": "n/a"},
    ]


def test_step_convert_cells_with_name():
    source = Resource(path="data/transform.csv")
    target = transform(source, steps=[steps.convert_cells(value="n/a", name="name")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "n/a", "population": 83},
        {"id": 2, "name": "n/a", "population": 66},
        {"id": 3, "name": "n/a", "population": 47},
    ]


# Format Cells


def test_step_format_cells():
    source = Resource(path="data/transform.csv")
    source.infer(only_sample=True)
    source.schema.get_field("id").type = "string"
    source.schema.get_field("population").type = "string"
    target = transform(source, steps=[steps.format_cells(template="Prefix: {0}")])
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": "Prefix: 1", "name": "Prefix: germany", "population": "Prefix: 83"},
        {"id": "Prefix: 2", "name": "Prefix: france", "population": "Prefix: 66"},
        {"id": "Prefix: 3", "name": "Prefix: spain", "population": "Prefix: 47"},
    ]


def test_step_format_cells_with_name():
    source = Resource(path="data/transform.csv")
    target = transform(
        source, steps=[steps.format_cells(template="Prefix: {0}", name="name")]
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "Prefix: germany", "population": 83},
        {"id": 2, "name": "Prefix: france", "population": 66},
        {"id": 3, "name": "Prefix: spain", "population": 47},
    ]
