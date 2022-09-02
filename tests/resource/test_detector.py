from frictionless import Resource, Schema, Detector


# General


def test_resource_detector_encoding_function():
    detector = Detector(encoding_function=lambda buffer: "utf-8")
    with Resource("data/table.csv", detector=detector) as resource:
        assert resource.encoding == "utf-8"
        assert resource.sample == [["id", "name"], ["1", "english"], ["2", "中国人"]]
        assert resource.fragment == [["1", "english"], ["2", "中国人"]]
        assert resource.header == ["id", "name"]


def test_resource_detector_field_type():
    detector = Detector(field_type="string")
    resource = Resource(path="data/table.csv", detector=detector)
    resource.infer(stats=True)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "name", "type": "string"},
        ]
    }
    assert resource.header == ["id", "name"]
    assert resource.read_rows() == [
        {"id": "1", "name": "english"},
        {"id": "2", "name": "中国人"},
    ]


def test_resource_detector_field_names():
    detector = Detector(field_names=["new1", "new2"])
    resource = Resource(path="data/table.csv", detector=detector)
    resource.infer(stats=True)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "new1", "type": "integer"},
            {"name": "new2", "type": "string"},
        ]
    }
    assert resource.labels == ["id", "name"]
    assert resource.header == ["new1", "new2"]
    assert resource.read_rows() == [
        {"new1": 1, "new2": "english"},
        {"new1": 2, "new2": "中国人"},
    ]


def test_resource_detector_field_float_numbers():
    data = [["number"], ["1.1"], ["2.2"], ["3.3"]]
    detector = Detector(field_float_numbers=True)
    resource = Resource(data=data, detector=detector)
    resource.infer(stats=True)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "number", "type": "number", "floatNumber": True},
        ]
    }
    assert resource.header == ["number"]
    assert resource.read_rows() == [
        {"number": 1.1},
        {"number": 2.2},
        {"number": 3.3},
    ]


def test_resource_detector_field_type_with_open():
    detector = Detector(field_type="string")
    with Resource("data/table.csv", detector=detector) as resource:
        assert resource.header == ["id", "name"]
        assert resource.schema.to_descriptor() == {
            "fields": [
                {"name": "id", "type": "string"},
                {"name": "name", "type": "string"},
            ]
        }
        assert resource.read_rows() == [
            {"id": "1", "name": "english"},
            {"id": "2", "name": "中国人"},
        ]


def test_resource_detector_field_names_with_open():
    detector = Detector(field_names=["new1", "new2"])
    with Resource("data/table.csv", detector=detector) as resource:
        assert resource.schema.to_descriptor() == {
            "fields": [
                {"name": "new1", "type": "integer"},
                {"name": "new2", "type": "string"},
            ]
        }
        assert resource.labels == ["id", "name"]
        assert resource.header == ["new1", "new2"]
        assert resource.read_rows() == [
            {"new1": 1, "new2": "english"},
            {"new1": 2, "new2": "中国人"},
        ]


def test_resource_detector_schema_sync():
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "name", "type": "string"},
                {"name": "id", "type": "integer"},
            ]
        }
    )
    detector = Detector(schema_sync=True)
    with Resource("data/sync-schema.csv", schema=schema, detector=detector) as resource:
        assert resource.schema == schema
        assert resource.sample == [["name", "id"], ["english", "1"], ["中国人", "2"]]
        assert resource.fragment == [["english", "1"], ["中国人", "2"]]
        assert resource.header == ["name", "id"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_detector_schema_sync_with_infer():
    schema = Schema.from_descriptor(
        {
            "fields": [
                {"name": "name", "type": "string"},
                {"name": "id", "type": "integer"},
            ]
        }
    )
    detector = Detector(schema_sync=True)
    resource = Resource(path="data/sync-schema.csv", schema=schema, detector=detector)
    resource.infer(stats=True)
    assert resource.schema == schema
    assert resource.sample == [["name", "id"], ["english", "1"], ["中国人", "2"]]
    assert resource.fragment == [["english", "1"], ["中国人", "2"]]
    assert resource.header == ["name", "id"]
    assert resource.read_rows() == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_resource_detector_schema_patch():
    detector = Detector(schema_patch={"fields": {"id": {"name": "ID", "type": "string"}}})
    with Resource("data/table.csv", detector=detector) as resource:
        assert resource.schema.to_descriptor() == {
            "fields": [
                {"name": "ID", "type": "string"},
                {"name": "name", "type": "string"},
            ]
        }
        assert resource.labels == ["id", "name"]
        assert resource.header == ["ID", "name"]
        assert resource.read_rows() == [
            {"ID": "1", "name": "english"},
            {"ID": "2", "name": "中国人"},
        ]


def test_resource_detector_schema_patch_missing_values():
    detector = Detector(schema_patch={"missingValues": ["1", "2"]})
    with Resource("data/table.csv", detector=detector) as resource:
        assert resource.header == ["id", "name"]
        assert resource.schema.to_descriptor() == {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ],
            "missingValues": ["1", "2"],
        }
        assert resource.read_rows() == [
            {"id": None, "name": "english"},
            {"id": None, "name": "中国人"},
        ]


def test_resource_detector_schema_patch_with_infer():
    detector = Detector(schema_patch={"fields": {"id": {"name": "ID", "type": "string"}}})
    resource = Resource(path="data/table.csv", detector=detector)
    resource.infer(stats=True)
    assert resource.schema.to_descriptor() == {
        "fields": [
            {"name": "ID", "type": "string"},
            {"name": "name", "type": "string"},
        ]
    }
    assert resource.labels == ["id", "name"]
    assert resource.header == ["ID", "name"]
    assert resource.read_rows() == [
        {"ID": "1", "name": "english"},
        {"ID": "2", "name": "中国人"},
    ]
