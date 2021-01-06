from frictionless import Resource, transform, steps


# Convert


def test_step_cell_convert():
    source = Resource(path="data/transform.csv")
    source.infer()
    source.schema.get_field("id").type = "string"
    source.schema.get_field("population").type = "string"
    target = transform(
        source,
        steps=[
            steps.cell_convert(value="n/a"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": "n/a", "name": "n/a", "population": "n/a"},
        {"id": "n/a", "name": "n/a", "population": "n/a"},
        {"id": "n/a", "name": "n/a", "population": "n/a"},
    ]


def test_step_cell_convert_with_field_name():
    source = Resource(path="data/transform.csv")
    source.infer()
    target = transform(
        source,
        steps=[
            steps.cell_convert(value="n/a", field_name="name"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "n/a", "population": 83},
        {"id": 2, "name": "n/a", "population": 66},
        {"id": 3, "name": "n/a", "population": 47},
    ]


# Fill


def test_step_cell_fill():
    source = Resource(path="data/transform.csv")
    source.infer()
    target = transform(
        source,
        steps=[
            steps.cell_replace(pattern="france", replace=None),
            steps.cell_fill(field_name="name", value="FRANCE"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "FRANCE", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_cell_fill_direction_down():
    source = Resource(path="data/transform.csv")
    source.infer()
    target = transform(
        source,
        steps=[
            steps.cell_replace(pattern="france", replace=None),
            steps.cell_fill(direction="down"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "germany", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_cell_fill_direction_right():
    source = Resource(path="data/transform.csv")
    source.infer()
    source.schema.get_field("id").type = "string"
    source.schema.get_field("population").type = "string"
    target = transform(
        source,
        steps=[
            steps.cell_replace(pattern="france", replace=None),
            steps.cell_fill(direction="right"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": "1", "name": "germany", "population": "83"},
        {"id": "2", "name": "2", "population": "66"},
        {"id": "3", "name": "spain", "population": "47"},
    ]


def test_step_cell_fill_direction_left():
    source = Resource(path="data/transform.csv")
    source.infer()
    source.schema.get_field("id").type = "string"
    source.schema.get_field("population").type = "string"
    target = transform(
        source,
        steps=[
            steps.cell_replace(pattern="france", replace=None),
            steps.cell_fill(direction="left"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": "1", "name": "germany", "population": "83"},
        {"id": "2", "name": "66", "population": "66"},
        {"id": "3", "name": "spain", "population": "47"},
    ]


# Format


def test_step_cell_format():
    source = Resource(path="data/transform.csv")
    source.infer()
    source.schema.get_field("id").type = "string"
    source.schema.get_field("population").type = "string"
    target = transform(
        source,
        steps=[
            steps.cell_format(template="Prefix: {0}"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": "Prefix: 1", "name": "Prefix: germany", "population": "Prefix: 83"},
        {"id": "Prefix: 2", "name": "Prefix: france", "population": "Prefix: 66"},
        {"id": "Prefix: 3", "name": "Prefix: spain", "population": "Prefix: 47"},
    ]


def test_step_cell_format_with_name():
    source = Resource(path="data/transform.csv")
    source.infer()
    target = transform(
        source,
        steps=[
            steps.cell_format(template="Prefix: {0}", field_name="name"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "Prefix: germany", "population": 83},
        {"id": 2, "name": "Prefix: france", "population": 66},
        {"id": 3, "name": "Prefix: spain", "population": 47},
    ]


# Interpolate


def test_step_cell_interpolate():
    source = Resource(path="data/transform.csv")
    source.infer()
    source.schema.get_field("id").type = "string"
    source.schema.get_field("population").type = "string"
    target = transform(
        source,
        steps=[
            steps.cell_interpolate(template="Prefix: %s"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": "Prefix: 1", "name": "Prefix: germany", "population": "Prefix: 83"},
        {"id": "Prefix: 2", "name": "Prefix: france", "population": "Prefix: 66"},
        {"id": "Prefix: 3", "name": "Prefix: spain", "population": "Prefix: 47"},
    ]


def test_step_cell_interpolate_with_name():
    source = Resource(path="data/transform.csv")
    source.infer()
    target = transform(
        source,
        steps=[
            steps.cell_interpolate(template="Prefix: %s", field_name="name"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "Prefix: germany", "population": 83},
        {"id": 2, "name": "Prefix: france", "population": 66},
        {"id": 3, "name": "Prefix: spain", "population": 47},
    ]


# Replace


def test_step_cell_replace():
    source = Resource(path="data/transform.csv")
    source.infer()
    target = transform(
        source,
        steps=[
            steps.cell_replace(pattern="france", replace="FRANCE"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "FRANCE", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_cell_replace_with_field_name():
    source = Resource(path="data/transform.csv")
    source.infer()
    target = transform(
        source,
        steps=[
            steps.cell_replace(pattern="france", replace="FRANCE", field_name="id"),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 83},
        {"id": 2, "name": "france", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


def test_step_cell_replace_using_regex():
    source = Resource(path="data/transform.csv")
    source.infer()
    target = transform(
        source,
        steps=[
            steps.cell_replace(
                pattern="<regex>.*r.*", replace="center", field_name="name"
            ),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "center", "population": 83},
        {"id": 2, "name": "center", "population": 66},
        {"id": 3, "name": "spain", "population": 47},
    ]


# Set


def test_step_cell_set():
    source = Resource(path="data/transform.csv")
    source.infer()
    target = transform(
        source,
        steps=[
            steps.cell_set(field_name="population", value=100),
        ],
    )
    assert target.schema == source.schema
    assert target.read_rows() == [
        {"id": 1, "name": "germany", "population": 100},
        {"id": 2, "name": "france", "population": 100},
        {"id": 3, "name": "spain", "population": 100},
    ]
