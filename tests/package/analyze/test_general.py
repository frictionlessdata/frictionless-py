from frictionless import Package, platform

IS_UNIX = platform.type != "windows"


# General


def test_analyze_package():
    package = Package("data/package-1067.json")
    analysis = package.analyze()
    assert len(analysis) == 3
    assert analysis["capital-valid"]["rows"] == 5
    assert list(analysis["capital-valid"].keys()) == [
        "variableTypes",
        "notNullRows",
        "rowsWithNullValues",
        "fieldStats",
        "averageRecordSizeInBytes",
        "timeTaken",
        "md5",
        "sha256",
        "bytes",
        "fields",
        "rows",
    ]
    assert analysis["capital-invalid"]["rows"] == 11
    assert list(analysis["capital-invalid"].keys()) == [
        "variableTypes",
        "notNullRows",
        "rowsWithNullValues",
        "fieldStats",
        "averageRecordSizeInBytes",
        "timeTaken",
        "md5",
        "sha256",
        "bytes",
        "fields",
        "rows",
    ]
    assert analysis["analysis-data"]["rows"] == 9
    assert list(analysis["analysis-data"].keys()) == [
        "variableTypes",
        "notNullRows",
        "rowsWithNullValues",
        "fieldStats",
        "averageRecordSizeInBytes",
        "timeTaken",
        "md5",
        "sha256",
        "bytes",
        "fields",
        "rows",
    ]


def test_analyze_package_detailed():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    assert analysis["capital-valid"]["rows"] == 5
    assert list(analysis["capital-valid"].keys()) == [
        "variableTypes",
        "notNullRows",
        "rowsWithNullValues",
        "fieldStats",
        "correlations",
        "averageRecordSizeInBytes",
        "timeTaken",
        "md5",
        "sha256",
        "bytes",
        "fields",
        "rows",
    ]
    assert analysis["capital-invalid"]["rows"] == 11
    assert list(analysis["capital-invalid"].keys()) == [
        "variableTypes",
        "notNullRows",
        "rowsWithNullValues",
        "fieldStats",
        "correlations",
        "averageRecordSizeInBytes",
        "timeTaken",
        "md5",
        "sha256",
        "bytes",
        "fields",
        "rows",
    ]
    assert analysis["analysis-data"]["rows"] == 9
    assert list(analysis["analysis-data"].keys()) == [
        "variableTypes",
        "notNullRows",
        "rowsWithNullValues",
        "fieldStats",
        "correlations",
        "averageRecordSizeInBytes",
        "timeTaken",
        "md5",
        "sha256",
        "bytes",
        "fields",
        "rows",
    ]


def test_analyze_package_invalid_data():
    descriptor = {
        "name": "capitals-and-schools",
        "resources": [
            {"name": "capital-invalid", "path": "data/invalid.csv"},
        ],
    }
    package = Package(descriptor)
    analysis = package.analyze()
    assert (
        round(analysis["capital-invalid"]["averageRecordSizeInBytes"]) == 12
        if IS_UNIX
        else 14
    )
    assert analysis["capital-invalid"]["fields"] == 4
    assert analysis["capital-invalid"]["fieldStats"] == {}
    assert analysis["capital-invalid"]["rows"] == 4
    assert analysis["capital-invalid"]["rowsWithNullValues"] == 3
    assert analysis["capital-invalid"]["notNullRows"] == 1
    assert analysis["capital-invalid"]["variableTypes"] == {}


def test_analyze_package_detailed_variable_types():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    assert len(analysis) == 3
    assert analysis["capital-valid"]["variableTypes"] == {
        "number": 1,
        "string": 1,
    }
    assert analysis["capital-invalid"]["variableTypes"] == {
        "integer": 1,
        "string": 1,
    }
    assert analysis["analysis-data"]["variableTypes"] == {
        "boolean": 2,
        "integer": 2,
        "number": 2,
        "string": 5,
    }


def test_analyze_package_detailed_non_numeric_values_summary():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    assert list(analysis["capital-valid"]["fieldStats"]["name"].keys()) == [
        "type",
        "values",
    ]
    assert list(analysis["capital-invalid"]["fieldStats"]["name"].keys()) == [
        "type",
        "values",
    ]
    assert list(analysis["analysis-data"]["fieldStats"]["gender"].keys()) == [
        "type",
        "values",
    ]


def test_analyze_package_detailed_numeric_values_descriptive_summary():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    assert list(analysis["analysis-data"]["fieldStats"]["parent_age"].keys()) == [
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
    name = "analysis-data"
    assert analysis[name]["fieldStats"]["parent_age"]["bounds"] == [39, 67]
    assert analysis[name]["fieldStats"]["parent_age"]["max"] == 57
    assert analysis[name]["fieldStats"]["parent_age"]["mean"] == 52.666666666666664
    assert analysis[name]["fieldStats"]["parent_age"]["median"] == 52
    assert analysis[name]["fieldStats"]["parent_age"]["min"] == 48
    assert analysis[name]["fieldStats"]["parent_age"]["missingValues"] == 0
    assert analysis[name]["fieldStats"]["parent_age"]["mode"] == 57
    assert analysis[name]["fieldStats"]["parent_age"]["quantiles"] == [49.5, 52.0, 56.5]
    assert analysis[name]["fieldStats"]["parent_age"]["stdev"] == 3.391164991562634
    assert analysis[name]["fieldStats"]["parent_age"]["uniqueValues"] == 7
    assert analysis[name]["fieldStats"]["parent_age"]["variance"] == 11.5
    assert analysis[name]["fieldStats"]["parent_age"]["outliers"] == []


def test_analyze_package_detailed_non_numeric_summary():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    assert analysis["capital-valid"]["fieldStats"]["name"]["type"] == "categorical"
    assert analysis["capital-valid"]["fieldStats"]["name"]["values"] == {
        "Berlin",
        "London",
        "Madrid",
        "Paris",
        "Rome",
    }
    assert (
        analysis["analysis-data"]["fieldStats"]["school_accreditation"]["type"]
        == "categorical"
    )
    assert analysis["analysis-data"]["fieldStats"]["school_accreditation"]["values"] == {
        "A",
        "B",
    }


def test_analyze_package_detailed_invalid_data():
    descriptor = {
        "name": "capitals-and-schools",
        "resources": [
            {"name": "capital-invalid", "path": "data/invalid.csv"},
        ],
    }
    package = Package(descriptor)
    analysis = package.analyze(detailed=True)
    name = "capital-invalid"
    assert round(analysis[name]["averageRecordSizeInBytes"]) == 12 if IS_UNIX else 14
    assert analysis[name]["fields"] == 4
    assert list(analysis[name]["fieldStats"].keys()) == [
        "id",
        "name",
        "field3",
        "name2",
    ]
    assert analysis[name]["rows"] == 4
    assert analysis[name]["rowsWithNullValues"] == 3
    assert analysis[name]["notNullRows"] == 1
    assert analysis[name]["variableTypes"] == {"integer": 3, "string": 1}
