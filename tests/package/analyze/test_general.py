from frictionless import Package


def test_analyze_package():
    package = Package("data/package-1067.json")
    analysis = package.analyze()
    assert len(analysis) == 3
    assert analysis["data/capital-valid.csv"]["rows"] == 5
    assert list(analysis["data/capital-valid.csv"].keys()) == [
        "variable_types",
        "not_null_rows",
        "rows_with_null_values",
        "field_stats",
        "average_record_size_in_bytes",
        "time_taken",
        "hash",
        "bytes",
        "fields",
        "rows",
    ]
    assert analysis["data/capital-invalid.csv"]["rows"] == 11
    assert list(analysis["data/capital-invalid.csv"].keys()) == [
        "variable_types",
        "not_null_rows",
        "rows_with_null_values",
        "field_stats",
        "average_record_size_in_bytes",
        "time_taken",
        "hash",
        "bytes",
        "fields",
        "rows",
    ]
    assert analysis["data/analysis-data.csv"]["rows"] == 9
    assert list(analysis["data/analysis-data.csv"].keys()) == [
        "variable_types",
        "not_null_rows",
        "rows_with_null_values",
        "field_stats",
        "average_record_size_in_bytes",
        "time_taken",
        "hash",
        "bytes",
        "fields",
        "rows",
    ]


def test_analyze_package_detailed():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    assert analysis["data/capital-valid.csv"]["rows"] == 5
    assert list(analysis["data/capital-valid.csv"].keys()) == [
        "variable_types",
        "not_null_rows",
        "rows_with_null_values",
        "field_stats",
        "correlations",
        "average_record_size_in_bytes",
        "time_taken",
        "hash",
        "bytes",
        "fields",
        "rows",
    ]
    assert analysis["data/capital-invalid.csv"]["rows"] == 11
    assert list(analysis["data/capital-valid.csv"].keys()) == [
        "variable_types",
        "not_null_rows",
        "rows_with_null_values",
        "field_stats",
        "correlations",
        "average_record_size_in_bytes",
        "time_taken",
        "hash",
        "bytes",
        "fields",
        "rows",
    ]
    assert analysis["data/analysis-data.csv"]["rows"] == 9
    assert list(analysis["data/analysis-data.csv"].keys()) == [
        "variable_types",
        "not_null_rows",
        "rows_with_null_values",
        "field_stats",
        "correlations",
        "average_record_size_in_bytes",
        "time_taken",
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
    assert round(analysis["data/invalid.csv"]["average_record_size_in_bytes"]) == 12
    assert analysis["data/invalid.csv"]["fields"] == 4
    assert analysis["data/invalid.csv"]["field_stats"] == {}
    assert analysis["data/invalid.csv"]["rows"] == 4
    assert analysis["data/invalid.csv"]["rows_with_null_values"] == 3
    assert analysis["data/invalid.csv"]["not_null_rows"] == 1
    assert analysis["data/invalid.csv"]["variable_types"] == {}


def test_analyze_package_detailed_variable_types():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    assert len(analysis) == 3
    assert analysis["data/capital-valid.csv"]["variable_types"] == {
        "number": 1,
        "string": 1,
    }
    assert analysis["data/capital-invalid.csv"]["variable_types"] == {
        "integer": 1,
        "string": 1,
    }
    assert analysis["data/analysis-data.csv"]["variable_types"] == {
        "boolean": 2,
        "integer": 2,
        "number": 2,
        "string": 5,
    }


def test_analyze_package_detailed_non_numeric_values_summary():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    assert list(analysis["data/capital-valid.csv"]["field_stats"]["name"].keys()) == [
        "type",
        "values",
    ]
    assert list(analysis["data/capital-invalid.csv"]["field_stats"]["name"].keys()) == [
        "type",
        "values",
    ]
    assert list(analysis["data/analysis-data.csv"]["field_stats"]["gender"].keys()) == [
        "type",
        "values",
    ]


def test_analyze_package_detailed_numeric_values_descriptive_summary():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    assert list(
        analysis["data/analysis-data.csv"]["field_stats"]["parent_age"].keys()
    ) == [
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
        "unique_values",
        "outliers",
        "missing_values",
    ]


def test_analyze_package_detailed_numeric_descriptive_statistics():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    assert analysis["data/analysis-data.csv"]["field_stats"]["parent_age"]["bounds"] == [
        39,
        67,
    ]
    assert analysis["data/analysis-data.csv"]["field_stats"]["parent_age"]["max"] == 57
    assert (
        analysis["data/analysis-data.csv"]["field_stats"]["parent_age"]["mean"]
        == 52.666666666666664
    )
    assert analysis["data/analysis-data.csv"]["field_stats"]["parent_age"]["median"] == 52
    assert analysis["data/analysis-data.csv"]["field_stats"]["parent_age"]["min"] == 48
    assert (
        analysis["data/analysis-data.csv"]["field_stats"]["parent_age"]["missing_values"]
        == 0
    )
    assert analysis["data/analysis-data.csv"]["field_stats"]["parent_age"]["mode"] == 57
    assert analysis["data/analysis-data.csv"]["field_stats"]["parent_age"][
        "quantiles"
    ] == [49.5, 52.0, 56.5]
    assert (
        analysis["data/analysis-data.csv"]["field_stats"]["parent_age"]["stdev"]
        == 3.391164991562634
    )
    assert (
        analysis["data/analysis-data.csv"]["field_stats"]["parent_age"]["unique_values"]
        == 7
    )
    assert (
        analysis["data/analysis-data.csv"]["field_stats"]["parent_age"]["variance"]
        == 11.5
    )
    assert (
        analysis["data/analysis-data.csv"]["field_stats"]["parent_age"]["outliers"] == []
    )


def test_analyze_package_detailed_non_numeric_summary():
    package = Package("data/package-1067.json")
    analysis = package.analyze(detailed=True)
    assert (
        analysis["data/capital-valid.csv"]["field_stats"]["name"]["type"] == "categorical"
    )
    assert analysis["data/capital-valid.csv"]["field_stats"]["name"]["values"] == {
        "Berlin",
        "London",
        "Madrid",
        "Paris",
        "Rome",
    }
    assert (
        analysis["data/analysis-data.csv"]["field_stats"]["school_accreditation"]["type"]
        == "categorical"
    )
    assert analysis["data/analysis-data.csv"]["field_stats"]["school_accreditation"][
        "values"
    ] == {
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
    assert round(analysis["data/invalid.csv"]["average_record_size_in_bytes"]) == 12
    assert analysis["data/invalid.csv"]["fields"] == 4
    assert list(analysis["data/invalid.csv"]["field_stats"].keys()) == [
        "id",
        "name",
        "field3",
        "name2",
    ]
    assert analysis["data/invalid.csv"]["rows"] == 4
    assert analysis["data/invalid.csv"]["rows_with_null_values"] == 3
    assert analysis["data/invalid.csv"]["not_null_rows"] == 1
    assert analysis["data/invalid.csv"]["variable_types"] == {"integer": 3, "string": 1}
