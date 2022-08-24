import pytest
from frictionless import Detector, Resource


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
    assert schema.to_descriptor() == {
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
    assert schema.to_descriptor() == {
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
    assert schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "string"},
            {"name": "name", "type": "string"},
        ],
    }


def test_schema_from_sparse_sample():
    labels = ["id", "age", "name"]
    sample = [
        ["1", "39", "Paul"],
        ["2", "23", "Jimmy"],
        ["3", "", "Jane"],
        ["4", "", "Judy"],
    ]
    detector = Detector(field_confidence=1)
    schema = detector.detect_schema(sample, labels=labels)
    assert schema.to_descriptor() == {
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "age", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }


def test_schema_infer_no_names():
    sample = [[1], [2], [3]]
    detector = Detector()
    schema = detector.detect_schema(sample)
    assert schema.to_descriptor() == {
        "fields": [{"name": "field1", "type": "integer"}],
    }


def test_detector_set_buffer_size():
    detector = Detector(buffer_size=10)
    assert detector.buffer_size == 10
    detector.buffer_size = 20
    assert detector.buffer_size == 20


def test_detector_set_sample_size():
    detector = Detector(sample_size=1000)
    assert detector.sample_size == 1000
    detector.sample_size = 800
    assert detector.sample_size == 800


def test_detector_set_encoding_function():
    enc_func = lambda buffer: "utf-8"
    detector = Detector(encoding_function=enc_func)
    assert detector.encoding_function == enc_func
    enc_func = lambda buffer: "utf-16"
    detector.encoding_function = enc_func
    assert detector.encoding_function == enc_func


def test_detector_set_encoding_confidence():
    detector = Detector(encoding_confidence=0.9)
    assert detector.encoding_confidence == 0.9
    detector.encoding_confidence = 0.8
    assert detector.encoding_confidence == 0.8


def test_detector_set_field_type():
    detector = Detector(field_type="string")
    assert detector.field_type == "string"
    detector.field_type = "int"
    assert detector.field_type == "int"


def test_detector_set_field_names():
    detector = Detector(field_names=["f1", "f2", "f3"])
    assert detector.field_names == ["f1", "f2", "f3"]
    detector.field_names = ["f1", "f2"]
    assert detector.field_names == ["f1", "f2"]


def test_detector_set_field_confidence():
    detector = Detector(field_confidence=0.8)
    assert detector.field_confidence == 0.8
    detector.field_confidence = 0.9
    assert detector.field_confidence == 0.9


def test_detector_set_field_float_numbers():
    detector = Detector(field_float_numbers=True)
    assert detector.field_float_numbers is True
    detector.field_float_numbers = False
    assert detector.field_float_numbers is False


def test_detector_set_field_missing_values():
    detector = Detector(field_missing_values=["", "67"])
    assert detector.field_missing_values == ["", "67"]
    detector.field_missing_values = ["", "70"]
    assert detector.field_missing_values == ["", "70"]


def test_detector_set_schema_sync():
    detector = Detector(schema_sync=True)
    assert detector.schema_sync is True
    detector.schema_sync = False
    assert detector.schema_sync is False


def test_detector_set_schema_patch():
    detector = Detector(schema_patch={"fields": {"id": {"type": "string"}}})
    assert detector.schema_patch == {"fields": {"id": {"type": "string"}}}
    detector.schema_patch = {"fields": {"age": {"type": "int"}}}
    assert detector.schema_patch == {"fields": {"age": {"type": "int"}}}


def test_detector_true_false_values():
    detector = Detector(field_true_values=["yes"], field_false_values=["no"])
    with Resource(
        "data/countries-truefalsevalues.csv",
        detector=detector,
    ) as resource:
        assert resource.schema.get_field("value").type == "boolean"
        assert resource.read_rows() == [
            {"id": 1, "value": True},
            {"id": 2, "value": False},
        ]


# Bugs


@pytest.mark.parametrize("confidence", [0.6, 0.7, 0.8])
def test_schema_from_synthetic_sparse_sample_issue_1050(confidence):

    # For each type (integer, number, string) there are example of
    # the type ("is") and examples of other type ("not")
    type_sample = {
        "integer": {"is": 1, "not": "string"},
        "number": {"is": 3.14, "not": "string"},
        "string": {"is": "string", "not": 1},
    }

    # Columns with type and confidence
    columns = [
        {"type": "integer", "conf": 0.7},
        {"type": "number", "conf": 1},
        {"type": "string", "conf": 1},
    ]

    def generate_rows(num_rows=100, columns=[]):
        rows = []
        num_per_type = [num_rows * c["conf"] for c in columns]
        for i in range(num_rows):
            row = []
            for ci, col in enumerate(columns):
                if i < num_per_type[ci]:
                    row.append(type_sample[col["type"]]["is"])
                else:
                    row.append(type_sample[col["type"]]["not"])
            rows.append(row)
        return rows

    fragment = generate_rows(columns=columns)
    detector = Detector(field_confidence=confidence)
    labels = [f"field{i}" for i in range(1, 4)]
    schema = detector.detect_schema(fragment, labels=labels)
    assert schema.to_descriptor() == {
        "fields": [
            {
                "name": f"field{i + 1}",
                "type": columns[i]["type"] if columns[i]["conf"] >= confidence else "any",
            }
            for i in range(len(columns))
        ],
    }
