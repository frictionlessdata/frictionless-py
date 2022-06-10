import types
from frictionless import extract, helpers


IS_UNIX = not helpers.is_platform("windows")


# General


def test_extract_package():
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    assert extract("data/package.json") == {
        path: [{"id": 1, "name": "english"}, {"id": 2, "name": "中国人"}]
    }


def test_extract_package_process():
    process = lambda row: row.to_list()
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    assert extract("data/package.json", process=process) == {
        path: [
            [1, "english"],
            [2, "中国人"],
        ],
    }


def test_extract_package_stream():
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    row_streams = extract("data/package.json", stream=True)
    row_stream = row_streams[path]
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_package_process_and_stream():
    process = lambda row: row.to_list()
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    list_streams = extract("data/package.json", process=process, stream=True)
    list_stream = list_streams[path]
    assert isinstance(list_stream, types.GeneratorType)
    assert list(list_stream) == [
        [1, "english"],
        [2, "中国人"],
    ]


def test_extract_package_descriptor_type_package():
    data = extract(descriptor="data/package/datapackage.json")
    assert isinstance(data, dict)


def test_extract_package_valid_rows_1004():
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    assert extract("data/package.json", valid=True) == {
        path: [{"id": 1, "name": "english"}, {"id": 2, "name": "中国人"}]
    }


def test_extract_package_process_valid_rows_1004():
    process = lambda row: row.to_list()
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    assert extract("data/package.json", process=process, valid=True) == {
        path: [
            [1, "english"],
            [2, "中国人"],
        ],
    }


def test_extract_package_stream_valid_rows_1004():
    path = "data/issue-1004-data1.csv" if IS_UNIX else "data\\issue-1004-data1.csv"
    row_streams = extract("data/issue-1004.package.json", stream=True, valid=True)
    print(row_streams)
    row_stream = row_streams[path]
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": "67"},
        {"id": 3, "neighbor_id": "22", "name": "Germany", "population": "83"},
        {"id": 4, "neighbor_id": None, "name": "Italy", "population": "60"},
    ]


def test_extract_package_stream_invalid_rows_1004():
    path = "data/issue-1004-data1.csv" if IS_UNIX else "data\\issue-1004-data1.csv"
    row_streams = extract("data/issue-1004.package.json", stream=True, valid=False)
    row_stream = row_streams[path]
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        {"id": 2, "neighbor_id": "3", "name": "France", "population": "n/a"},
        {"id": 5, "neighbor_id": None, "name": None, "population": None},
    ]


def test_extract_package_process_stream_valid_rows_1004():
    process = lambda row: row.to_list()
    path = "data/issue-1004-data1.csv" if IS_UNIX else "data\\issue-1004-data1.csv"
    list_streams = extract(
        "data/issue-1004.package.json",
        process=process,
        stream=True,
        valid=False,
    )
    list_stream = list_streams[path]
    assert isinstance(list_stream, types.GeneratorType)
    assert list(list_stream) == [[2, "3", "France", "n/a"], [5, None, None, None]]


def test_extract_package_valid_rows_with_multiple_resources_1004():
    path1 = "data/issue-1004-data1.csv" if IS_UNIX else "data\\issue-1004-data1.csv"
    path2 = "data/issue-1004-data2.csv" if IS_UNIX else "data\\issue-1004-data2.csv"
    output = extract("data/issue-1004.package.json", valid=True)
    assert output[path1] == [
        {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": "67"},
        {"id": 3, "neighbor_id": "22", "name": "Germany", "population": "83"},
        {"id": 4, "neighbor_id": None, "name": "Italy", "population": "60"},
    ]
    assert output[path2] == []


def test_extract_package_invalid_rows_with_multiple_resources_1004():
    path1 = "data/issue-1004-data1.csv" if IS_UNIX else "data\\issue-1004-data1.csv"
    path2 = "data/issue-1004-data2.csv" if IS_UNIX else "data\\issue-1004-data2.csv"
    output = extract("data/issue-1004.package.json", valid=False)
    assert output[path1] == [
        {"id": 2, "neighbor_id": "3", "name": "France", "population": "n/a"},
        {"id": 5, "neighbor_id": None, "name": None, "population": None},
    ]
    assert output[path2] == [
        {"id": 1, "name": "english", "country": None, "city": None},
        {"id": 1, "name": "english", "country": None, "city": None},
        {"id": None, "name": None, "country": None, "city": None},
        {"id": 2, "name": "german", "country": 1, "city": 2},
    ]


def test_extract_package_no_valid_rows_1004():
    path = "data/issue-1004-data2.csv" if IS_UNIX else "data\\issue-1004-data2.csv"
    output = extract("data/issue-1004.package.json", valid=True)
    assert output[path] == []


def test_extract_package_no_invalid_rows_1004():
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    output = extract("data/package.json", valid=False)
    assert output[path] == []
