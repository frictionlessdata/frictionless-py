from frictionless import Detector


# General


def test_schema_from_sample():
    labels = ["id", "age", "name"]
    sample = [
        ["1", "39", "Paul"],
        ["2", "23", "Jimmy"],
        ["3", "36", "Jane"],
        ["4", "N/A", "Judy"],
    ]
    detector = Detector()
    schema = detector.detect_schema(sample, labels=labels)
    assert schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "string"},
            {"name": "name", "type": "string"},
        ],
    }


def test_schema_from_sample_confidence_less():
    labels = ["id", "age", "name"]
    sample = [
        ["1", "39", "Paul"],
        ["2", "23", "Jimmy"],
        ["3", "36", "Jane"],
        ["4", "N/A", "Judy"],
    ]
    detector = Detector(field_confidence=0.75)
    schema = detector.detect_schema(sample, labels=labels)
    assert schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }


def test_schema_from_sample_confidence_full():
    labels = ["id", "age", "name"]
    sample = [
        ["1", "39", "Paul"],
        ["2", "23", "Jimmy"],
        ["3", "36", "Jane"],
        ["4", "N/A", "Judy"],
    ]
    detector = Detector(field_confidence=1)
    schema = detector.detect_schema(sample, labels=labels)
    assert schema == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "string"},
            {"name": "name", "type": "string"},
        ],
    }


def test_schema_infer_no_names():
    sample = [[1], [2], [3]]
    detector = Detector()
    schema = detector.detect_schema(sample)
    assert schema == {
        "fields": [{"name": "field1", "type": "integer"}],
    }
