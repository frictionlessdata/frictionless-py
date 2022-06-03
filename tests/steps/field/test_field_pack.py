from frictionless import Resource, transform, steps


def test_step_field_pack_907():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[steps.field_pack(name="details", from_names=["name", "population"])],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "details", "type": "array"},
        ]
    }
    assert target.read_rows()[0] == {
        "id": 1,
        "details": ["germany", "83"],
    }


def test_step_field_pack_header_preserve_907():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.field_pack(
                name="details", from_names=["name", "population"], preserve=True
            )
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "details", "type": "array"},
        ]
    }
    assert target.read_rows()[0] == {
        "id": 1,
        "name": "germany",
        "population": 83,
        "details": ["germany", "83"],
    }


def test_step_field_pack_object_907():
    source = Resource("data/transform.csv")
    target = source.transform(
        steps=[
            steps.field_pack(
                name="details",
                from_names=["name", "population"],
                field_type="object",
                preserve=True,
            )
        ],
    )
    assert target.schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
            {"name": "population", "type": "integer"},
            {"name": "details", "type": "object"},
        ]
    }
    assert target.read_rows()[0] == {
        "id": 1,
        "name": "germany",
        "population": 83,
        "details": {"name": "germany", "population": "83"},
    }
