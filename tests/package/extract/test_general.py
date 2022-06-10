import types
from frictionless import Package, helpers


IS_UNIX = not helpers.is_platform("windows")


# General


def test_extract_package():
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    package = Package(path)
    assert package.extract() == {
        path: [{"id": 1, "name": "english"}, {"id": 2, "name": "中国人"}]
    }


def test_extract_package_process():
    process = lambda row: row.to_list()
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    package = Package(path)
    assert package.extract(process=process) == {
        path: [
            [1, "english"],
            [2, "中国人"],
        ],
    }


def test_extract_package_stream():
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    package = Package(path)
    row_streams = package.extract(stream=True)
    row_stream = row_streams[path]
    assert isinstance(row_stream, types.GeneratorType)
    assert list(row_stream) == [
        {"id": 1, "name": "english"},
        {"id": 2, "name": "中国人"},
    ]


def test_extract_package_process_and_stream():
    process = lambda row: row.to_list()
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    package = Package(path)
    list_streams = package.extract(process=process, stream=True)
    list_stream = list_streams[path]
    assert isinstance(list_stream, types.GeneratorType)
    assert list(list_stream) == [
        [1, "english"],
        [2, "中国人"],
    ]


def test_extract_package_descriptor_type_package():
    package = Package(descriptor="data/package/datapackage.json")
    data = package.extract()
    assert isinstance(data, dict)


def test_extract_package_valid_rows_1004():
    path1 = "data/issue-1004-data1.csv" if IS_UNIX else "data\\issue-1004-data1.csv"
    path2 = "data/issue-1004-data2.csv" if IS_UNIX else "data\\issue-1004-data2.csv"
    package = Package("data/issue-1004.package.json")
    output = package.extract(valid=True)
    assert output == {
        path1: [
            {"id": 1, "neighbor_id": "Ireland", "name": "Britain", "population": "67"},
            {"id": 3, "neighbor_id": "22", "name": "Germany", "population": "83"},
            {"id": 4, "neighbor_id": None, "name": "Italy", "population": "60"},
        ],
        path2: [],
    }


def test_extract_package_invalid_rows_1004():
    path1 = "data/issue-1004-data1.csv" if IS_UNIX else "data\\issue-1004-data1.csv"
    path2 = "data/issue-1004-data2.csv" if IS_UNIX else "data\\issue-1004-data2.csv"
    package = Package("data/issue-1004.package.json")
    output = package.extract(valid=False)
    assert output == {
        path1: [
            {"id": 2, "neighbor_id": "3", "name": "France", "population": "n/a"},
            {"id": 5, "neighbor_id": None, "name": None, "population": None},
        ],
        path2: [
            {"id": 1, "name": "english", "country": None, "city": None},
            {"id": 1, "name": "english", "country": None, "city": None},
            {"id": None, "name": None, "country": None, "city": None},
            {"id": 2, "name": "german", "country": 1, "city": 2},
        ],
    }


def test_extract_package_process_stream_valid_rows_1004():
    path = "data/issue-1004-data1.csv" if IS_UNIX else "data\\issue-1004-data1.csv"
    process = lambda row: row.to_list()
    package = Package("data/issue-1004.package.json")
    list_streams = package.extract(process=process, stream=True, valid=True)
    list_stream = list_streams[path]
    assert isinstance(list_stream, types.GeneratorType)
    assert list(list_stream) == [
        [1, "Ireland", "Britain", "67"],
        [3, "22", "Germany", "83"],
        [4, None, "Italy", "60"],
    ]


def test_extract_package_no_valid_rows_1004():
    path = "data/issue-1004-data2.csv" if IS_UNIX else "data\\issue-1004-data2.csv"
    package = Package("data/issue-1004.package.json")
    output = package.extract(valid=True)
    assert output[path] == []


def test_extract_package_no_invalid_rows_1004():
    path = "data/table.csv" if IS_UNIX else "data\\table.csv"
    package = Package("data/package.json")
    output = package.extract(valid=False)
    assert output[path] == []
