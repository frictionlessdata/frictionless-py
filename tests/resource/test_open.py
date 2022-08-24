import pytest
from frictionless import Resource, Dialect, Detector, FrictionlessException


# General


def test_resource_open():
    with Resource("data/table.csv") as resource:
        assert resource.name == "table"
        assert resource.path == "data/table.csv"
        assert resource.normpath == "data/table.csv"
        assert resource.scheme == "file"
        assert resource.format == "csv"
        assert resource.encoding == "utf-8"
        assert resource.innerpath == None
        assert resource.compression == None
        assert resource.sample == [["id", "name"], ["1", "english"], ["2", "中国人"]]
        assert resource.fragment == [["1", "english"], ["2", "中国人"]]
        assert resource.header == ["id", "name"]
        assert resource.header.row_numbers == [1]
        assert resource.schema.to_descriptor() == {
            "fields": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "string"},
            ]
        }
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_open_read_rows():
    with Resource("data/table.csv") as resource:
        headers = resource.header
        row1, row2 = resource.read_rows()
        assert headers == ["id", "name"]
        assert headers.field_numbers == [1, 2]
        assert headers.errors == []
        assert headers.valid is True
        assert row1.to_dict() == {"id": 1, "name": "english"}
        assert row1.field_numbers == [1, 2]
        assert row1.row_number == 2
        assert row1.errors == []
        assert row1.valid is True
        assert row2.to_dict() == {"id": 2, "name": "中国人"}
        assert row2.field_numbers == [1, 2]
        assert row2.row_number == 3
        assert row2.errors == []
        assert row2.valid is True


def test_resource_open_row_stream():
    with Resource("data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        assert list(resource.row_stream) == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]
        assert list(resource.row_stream) == []


def test_resource_open_row_stream_iterate():
    with Resource("data/table.csv") as resource:
        assert resource.header == ["id", "name"]
        for row in resource.row_stream:
            assert len(row) == 2
            assert row.row_number in [2, 3]
            if row.row_number == 2:
                assert row.to_dict() == {"id": 1, "name": "english"}
            if row.row_number == 3:
                assert row.to_dict() == {"id": 2, "name": "中国人"}


def test_resource_open_row_stream_error_cells():
    detector = Detector(field_type="integer")
    with Resource("data/table.csv", detector=detector) as resource:
        row1, row2 = resource.read_rows()
        assert resource.header == ["id", "name"]
        assert row1.errors[0].type == "type-error"
        assert row1.error_cells == {"name": "english"}
        assert row1.to_dict() == {"id": 1, "name": None}
        assert row1.valid is False
        assert row2.errors[0].type == "type-error"
        assert row2.error_cells == {"name": "中国人"}
        assert row2.to_dict() == {"id": 2, "name": None}
        assert row2.valid is False


def test_resource_open_row_stream_blank_cells():
    detector = Detector(schema_patch={"missingValues": ["1", "2"]})
    with Resource("data/table.csv", detector=detector) as resource:
        row1, row2 = resource.read_rows()
        assert resource.header == ["id", "name"]
        assert row1.blank_cells == {"id": "1"}
        assert row1.to_dict() == {"id": None, "name": "english"}
        assert row1.valid is True
        assert row2.blank_cells == {"id": "2"}
        assert row2.to_dict() == {"id": None, "name": "中国人"}
        assert row2.valid is True


def test_resource_open_read_cells():
    with Resource("data/table.csv") as resource:
        assert resource.read_cells() == [
            ["id", "name"],
            ["1", "english"],
            ["2", "中国人"],
        ]


def test_resource_open_cell_stream():
    with Resource("data/table.csv") as resource:
        assert list(resource.cell_stream) == [
            ["id", "name"],
            ["1", "english"],
            ["2", "中国人"],
        ]
        assert list(resource.cell_stream) == []


def test_resource_open_cell_stream_iterate():
    with Resource("data/table.csv") as resource:
        for number, cells in enumerate(resource.cell_stream):
            assert len(cells) == 2
            if number == 0:
                assert cells == ["id", "name"]
            if number == 1:
                assert cells == ["1", "english"]
            if number == 2:
                assert cells == ["2", "中国人"]


def test_resource_open_empty():
    with Resource("data/empty.csv") as resource:
        assert resource.header.missing
        assert resource.header == []
        assert resource.schema.to_descriptor() == {"fields": []}
        assert resource.read_rows() == []


def test_resource_open_without_rows():
    with Resource("data/without-rows.csv") as resource:
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == []
        assert resource.schema.to_descriptor() == {
            "fields": [
                {"name": "id", "type": "any"},
                {"name": "name", "type": "any"},
            ]
        }


def test_resource_open_without_headers():
    dialect = Dialect(header=False)
    with Resource("data/without-headers.csv", dialect=dialect) as resource:
        assert resource.labels == []
        assert resource.header.missing
        assert resource.header == ["field1", "field2"]
        assert resource.schema.to_descriptor() == {
            "fields": [
                {"name": "field1", "type": "integer"},
                {"name": "field2", "type": "string"},
            ]
        }
        assert resource.read_rows() == [
            {"field1": 1, "field2": "english"},
            {"field1": 2, "field2": "中国人"},
            {"field1": 3, "field2": "german"},
        ]


def test_resource_open_source_error_data():
    resource = Resource(b"[1,2]", type="table", format="json")
    with pytest.raises(FrictionlessException) as excinfo:
        resource.open()
    error = excinfo.value.error
    assert error.type == "source-error"
    assert error.note == "unsupported inline data"


def test_resource_reopen():
    with Resource("data/table.csv") as resource:

        # Open
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]

        # Re-open
        resource.open()
        assert resource.header == ["id", "name"]
        assert resource.read_rows() == [
            {"id": 1, "name": "english"},
            {"id": 2, "name": "中国人"},
        ]


def test_resource_reopen_and_detector_sample_size():
    detector = Detector(sample_size=3)
    with Resource("data/long.csv", detector=detector) as resource:
        # Before reset
        assert resource.sample == [["id", "name"], ["1", "a"], ["2", "b"]]
        assert resource.fragment == [["1", "a"], ["2", "b"]]
        assert resource.read_rows() == [
            {"id": 1, "name": "a"},
            {"id": 2, "name": "b"},
            {"id": 3, "name": "c"},
            {"id": 4, "name": "d"},
            {"id": 5, "name": "e"},
            {"id": 6, "name": "f"},
        ]
        # Re-open
        resource.open()
        # After reopen
        assert resource.sample == [["id", "name"], ["1", "a"], ["2", "b"]]
        assert resource.fragment == [["1", "a"], ["2", "b"]]
        assert resource.read_rows() == [
            {"id": 1, "name": "a"},
            {"id": 2, "name": "b"},
            {"id": 3, "name": "c"},
            {"id": 4, "name": "d"},
            {"id": 5, "name": "e"},
            {"id": 6, "name": "f"},
        ]


def test_resource_reopen_generator():
    def generator():
        yield [1]
        yield [2]

    dialect = Dialect(header=False)
    with Resource(generator, dialect=dialect) as resource:
        # Before reopen
        assert resource.read_rows() == [{"field1": 1}, {"field1": 2}]
        # Reset resource
        resource.open()
        # After reopen
        assert resource.read_rows() == [{"field1": 1}, {"field1": 2}]
