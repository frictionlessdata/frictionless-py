from frictionless import Package, helpers


IS_UNIX = not helpers.is_platform("windows")


def test_analyze_package():
    package = Package("data/package-1067.json")
    analysis = package.analyze()
    assert len(analysis) == 3
    path_1 = "data/capital-valid.csv" if IS_UNIX else "data\\capital-valid.csv"
    path_2 = "data/capital-invalid.csv" if IS_UNIX else "data\\capital-invalid.csv"
    path_3 = "data/analysis-data.csv" if IS_UNIX else "data\\analysis-data.csv"
    assert analysis[path_1]["rows"] == 5
    assert list(analysis[path_1].keys()) == [
        "variableTypes",
        "notNullRows",
        "rowsWithNullValues",
        "fieldStats",
        "averageRecordSizeInBytes",
        "timeTaken",
        "hash",
        "bytes",
        "fields",
        "rows",
    ]
    assert analysis[path_2]["rows"] == 11
    assert list(analysis[path_2].keys()) == [
        "variableTypes",
        "notNullRows",
        "rowsWithNullValues",
        "fieldStats",
        "averageRecordSizeInBytes",
        "timeTaken",
        "hash",
        "bytes",
        "fields",
        "rows",
    ]
    assert analysis[path_3]["rows"] == 9
    assert list(analysis[path_3].keys()) == [
        "variableTypes",
        "notNullRows",
        "rowsWithNullValues",
        "fieldStats",
        "averageRecordSizeInBytes",
        "timeTaken",
        "hash",
        "bytes",
        "fields",
        "rows",
    ]


def test_analyze_package_detailed():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    path_1 = "data/capital-valid.csv" if IS_UNIX else "data\\capital-valid.csv"
    path_2 = "data/capital-invalid.csv" if IS_UNIX else "data\\capital-invalid.csv"
    path_3 = "data/analysis-data.csv" if IS_UNIX else "data\\analysis-data.csv"
    assert analysis[path_1]["rows"] == 5
    assert list(analysis[path_1].keys()) == [
        "variableTypes",
        "notNullRows",
        "rowsWithNullValues",
        "fieldStats",
        "correlations",
        "averageRecordSizeInBytes",
        "timeTaken",
        "hash",
        "bytes",
        "fields",
        "rows",
    ]
    assert analysis[path_2]["rows"] == 11
    assert list(analysis[path_2].keys()) == [
        "variableTypes",
        "notNullRows",
        "rowsWithNullValues",
        "fieldStats",
        "correlations",
        "averageRecordSizeInBytes",
        "timeTaken",
        "hash",
        "bytes",
        "fields",
        "rows",
    ]
    assert analysis[path_3]["rows"] == 9
    assert list(analysis[path_3].keys()) == [
        "variableTypes",
        "notNullRows",
        "rowsWithNullValues",
        "fieldStats",
        "correlations",
        "averageRecordSizeInBytes",
        "timeTaken",
        "hash",
        "bytes",
        "fields",
        "rows",
    ]


def test_analyze_package_invalid_data():
    descriptor = {
        "name": "capitals and schools",
        "resources": [
            {"name": "capital-invalid", "path": "data/invalid.csv"},
        ],
    }
    package = Package(descriptor)
    analysis = package.analyze()
    assert (
        round(analysis["data/invalid.csv"]["averageRecordSizeInBytes"]) == 12
        if IS_UNIX
        else 14
    )
    assert analysis["data/invalid.csv"]["fields"] == 4
    assert analysis["data/invalid.csv"]["fieldStats"] == {}
    assert analysis["data/invalid.csv"]["rows"] == 4
    assert analysis["data/invalid.csv"]["rowsWithNullValues"] == 3
    assert analysis["data/invalid.csv"]["notNullRows"] == 1
    assert analysis["data/invalid.csv"]["variableTypes"] == {}


def test_analyze_package_detailed_variable_types():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    path_1 = "data/capital-valid.csv" if IS_UNIX else "data\\capital-valid.csv"
    path_2 = "data/capital-invalid.csv" if IS_UNIX else "data\\capital-invalid.csv"
    path_3 = "data/analysis-data.csv" if IS_UNIX else "data\\analysis-data.csv"
    assert len(analysis) == 3
    assert analysis[path_1]["variableTypes"] == {
        "number": 1,
        "string": 1,
    }
    assert analysis[path_2]["variableTypes"] == {
        "integer": 1,
        "string": 1,
    }
    assert analysis[path_3]["variableTypes"] == {
        "boolean": 2,
        "integer": 2,
        "number": 2,
        "string": 5,
    }


def test_analyze_package_detailed_non_numeric_values_summary():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    path_1 = "data/capital-valid.csv" if IS_UNIX else "data\\capital-valid.csv"
    path_2 = "data/capital-invalid.csv" if IS_UNIX else "data\\capital-invalid.csv"
    path_3 = "data/analysis-data.csv" if IS_UNIX else "data\\analysis-data.csv"
    assert list(analysis[path_1]["fieldStats"]["name"].keys()) == [
        "type",
        "values",
    ]
    assert list(analysis[path_2]["fieldStats"]["name"].keys()) == [
        "type",
        "values",
    ]
    assert list(analysis[path_3]["fieldStats"]["gender"].keys()) == [
        "type",
        "values",
    ]


def test_analyze_package_detailed_numeric_values_descriptive_summary():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    path = "data/analysis-data.csv" if IS_UNIX else "data\\analysis-data.csv"
    assert list(analysis[path]["fieldStats"]["parent_age"].keys()) == [
        "type",
        "mean",
        "median",
        "mode",
        "variance",
        "quantiles",
        "stdev",
        "max",
        "min",
        "bounds",
        "uniqueValues",
        "outliers",
        "missingValues",
    ]


def test_analyze_package_detailed_numeric_descriptive_statistics():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    path = "data/analysis-data.csv" if IS_UNIX else "data\\analysis-data.csv"
    assert analysis[path]["fieldStats"]["parent_age"]["bounds"] == [
        39,
        67,
    ]
    assert analysis[path]["fieldStats"]["parent_age"]["max"] == 57
    assert analysis[path]["fieldStats"]["parent_age"]["mean"] == 52.666666666666664
    assert analysis[path]["fieldStats"]["parent_age"]["median"] == 52
    assert analysis[path]["fieldStats"]["parent_age"]["min"] == 48
    assert analysis[path]["fieldStats"]["parent_age"]["missingValues"] == 0
    assert analysis[path]["fieldStats"]["parent_age"]["mode"] == 57
    assert analysis[path]["fieldStats"]["parent_age"]["quantiles"] == [49.5, 52.0, 56.5]
    assert analysis[path]["fieldStats"]["parent_age"]["stdev"] == 3.391164991562634
    assert analysis[path]["fieldStats"]["parent_age"]["uniqueValues"] == 7
    assert analysis[path]["fieldStats"]["parent_age"]["variance"] == 11.5
    assert analysis[path]["fieldStats"]["parent_age"]["outliers"] == []


def test_analyze_package_detailed_non_numeric_summary():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    path_1 = "data/capital-valid.csv" if IS_UNIX else "data\\capital-valid.csv"
    path_2 = "data/analysis-data.csv" if IS_UNIX else "data\\analysis-data.csv"
    assert analysis[path_1]["fieldStats"]["name"]["type"] == "categorical"
    assert analysis[path_1]["fieldStats"]["name"]["values"] == {
        "Berlin",
        "London",
        "Madrid",
        "Paris",
        "Rome",
    }
    assert analysis[path_2]["fieldStats"]["school_accreditation"]["type"] == "categorical"
    assert analysis[path_2]["fieldStats"]["school_accreditation"]["values"] == {
        "A",
        "B",
    }


def test_analyze_package_detailed_invalid_data():
    descriptor = {
        "name": "capitals and schools",
        "resources": [
            {"name": "capital-invalid", "path": "data/invalid.csv"},
        ],
    }
    package = Package(descriptor)
    analysis = package.analyze(detailed=True)
    path = "data/invalid.csv"
    assert round(analysis[path]["averageRecordSizeInBytes"]) == 12 if IS_UNIX else 14
    assert analysis[path]["fields"] == 4
    assert list(analysis[path]["fieldStats"].keys()) == [
        "id",
        "name",
        "field3",
        "name2",
    ]
    assert analysis[path]["rows"] == 4
    assert analysis[path]["rowsWithNullValues"] == 3
    assert analysis[path]["notNullRows"] == 1
    assert analysis[path]["variableTypes"] == {"integer": 3, "string": 1}
