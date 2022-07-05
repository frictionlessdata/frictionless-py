from frictionless import Resource, helpers


IS_UNIX = not helpers.is_platform("windows")


def test_analyze_resource():
    resource = Resource({"path": "data/analysis-data.csv"})
    analysis = resource.analyze()
    assert list(analysis.keys()) == [
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
    assert round(analysis["average_record_size_in_bytes"]) == 85 if IS_UNIX else 86
    assert analysis["fields"] == 11
    assert analysis["rows"] == 9
    assert analysis["rows_with_null_values"] == 2
    assert analysis["not_null_rows"] == 7
    assert analysis["variable_types"] == {}


def test_analyze_resource_detailed():
    resource = Resource({"path": "data/analysis-data.csv"})
    analysis = resource.analyze(detailed=True)
    assert list(analysis.keys()) == [
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
    assert round(analysis["average_record_size_in_bytes"]) == 85 if IS_UNIX else 86
    assert analysis["fields"] == 11
    assert analysis["rows"] == 9
    assert analysis["rows_with_null_values"] == 2
    assert analysis["not_null_rows"] == 7
    assert analysis["variable_types"] == {
        "boolean": 2,
        "integer": 2,
        "number": 2,
        "string": 5,
    }


def test_analyze_resource_detailed_non_numeric_values_summary():
    resource = Resource({"path": "data/analysis-data.csv"})
    analysis = resource.analyze(detailed=True)
    assert list(analysis["field_stats"]["gender"].keys()) == ["type", "values"]


def test_analyze_resource_detailed_numeric_values_descriptive_summray():
    resource = Resource({"path": "data/analysis-data.csv"})
    analysis = resource.analyze(detailed=True)
    assert list(analysis["field_stats"]["parent_age"].keys()) == [
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


def test_analyze_resource_detailed_numeric_descriptive_statistics():
    resource = Resource({"path": "data/analysis-data.csv"})
    analysis = resource.analyze(detailed=True)
    assert analysis["field_stats"]["parent_age"]["bounds"] == [39, 67]
    assert analysis["field_stats"]["parent_age"]["max"] == 57
    assert analysis["field_stats"]["parent_age"]["mean"] == 52.666666666666664
    assert analysis["field_stats"]["parent_age"]["median"] == 52
    assert analysis["field_stats"]["parent_age"]["min"] == 48
    assert analysis["field_stats"]["parent_age"]["missing_values"] == 0
    assert analysis["field_stats"]["parent_age"]["mode"] == 57
    assert analysis["field_stats"]["parent_age"]["quantiles"] == [49.5, 52.0, 56.5]
    assert analysis["field_stats"]["parent_age"]["stdev"] == 3.391164991562634
    assert analysis["field_stats"]["parent_age"]["unique_values"] == 7
    assert analysis["field_stats"]["parent_age"]["variance"] == 11.5
    assert analysis["field_stats"]["parent_age"]["outliers"] == []


def test_analyze_resource_detailed_numeric_descriptive_statistics_with_missing_values():
    resource = Resource({"path": "data/analysis-data.csv"})
    analysis = resource.analyze(detailed=True)
    assert analysis["field_stats"]["average_grades"]["bounds"] == [81, 96]
    assert analysis["field_stats"]["average_grades"]["max"] == 10000.0
    assert analysis["field_stats"]["average_grades"]["mean"] == 1503.28
    assert analysis["field_stats"]["average_grades"]["median"] == 86.91
    assert analysis["field_stats"]["average_grades"]["min"] == 84.65
    assert analysis["field_stats"]["average_grades"]["missing_values"] == 2
    assert analysis["field_stats"]["average_grades"]["mode"] == 86.79
    assert analysis["field_stats"]["average_grades"]["quantiles"] == [86.79, 86.91, 90.39]
    assert round(analysis["field_stats"]["average_grades"]["stdev"]) == 3747
    assert analysis["field_stats"]["average_grades"]["unique_values"] == 6
    assert round(analysis["field_stats"]["average_grades"]["variance"]) == 14037774
    assert analysis["field_stats"]["average_grades"]["outliers"] == [10000.0]


def test_analyze_resource_detailed_descriptive_statistics_with_outliers():
    resource = Resource({"path": "data/analysis-data.csv"})
    analysis = resource.analyze(detailed=True)
    assert analysis["field_stats"]["average_grades"]["bounds"] == [81, 96]
    assert analysis["field_stats"]["average_grades"]["outliers"] == [10000.0]


def test_analyze_resource_detailed_descriptive_statistics_variables_correlation():
    resource = Resource({"path": "data/analysis-data.csv"})
    analysis = resource.analyze(detailed=True)
    assert list(analysis["correlations"].keys()) == [
        "parent_age",
        "parent_salary",
        "house_area",
        "average_grades",
    ]
    assert (
        analysis["correlations"]["average_grades"][0]["field_name"] == "parent_age"
        and analysis["correlations"]["average_grades"][0]["corr"] == -0.09401771232099933
    )
    assert (
        analysis["correlations"]["average_grades"][1]["field_name"] == "parent_salary"
        and analysis["correlations"]["average_grades"][1]["corr"] == 0.4241304392492213
    )
    assert (
        analysis["correlations"]["average_grades"][2]["field_name"] == "house_area"
        and analysis["correlations"]["average_grades"][2]["corr"] == 0.14354348594097088
    )
    assert (
        analysis["correlations"]["average_grades"][3]["field_name"] == "average_grades"
        and analysis["correlations"]["average_grades"][3]["corr"] == 1.0
    )


def test_analyze_resource_detailed_non_numeric_summary():
    resource = Resource({"path": "data/analysis-data.csv"})
    analysis = resource.analyze(detailed=True)
    assert list(analysis["field_stats"]["gender"].keys()) == ["type", "values"]
    assert analysis["field_stats"]["gender"]["values"] == {"Male", "Female"}


def test_analyze_resource_detailed_non_numeric_data_identification():
    data = [
        ["gender", "country"],
        ["male", "usa"],
        ["female", "usa"],
        ["male", "italy"],
        ["female", "italy"],
        ["female", "italy"],
    ]
    resource = Resource(data)
    analysis = resource.analyze(detailed=True)
    assert analysis["field_stats"]["gender"]["type"] == "categorical"
    assert analysis["field_stats"]["gender"]["values"] == {"male", "female"}
    assert analysis["field_stats"]["country"]["type"] == "categorical"
    assert analysis["field_stats"]["country"]["values"] == {"usa", "italy"}


def test_analyze_resource_with_empty_rows():
    data = [["a", "b"]]
    resource = Resource(data)
    analysis = resource.analyze()
    assert list(analysis.keys()) == [
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
    assert analysis["rows"] == 0


def test_analyze_resource_detailed_with_empty_rows():
    data = [["a", "b"]]
    resource = Resource(data)
    analysis = resource.analyze(detailed=True)
    assert list(analysis.keys()) == [
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
    assert analysis["rows"] == 0


def test_analyze_resource_with_invalid_data():
    resource = Resource({"path": "data/invalid.csv"})
    analysis = resource.analyze()
    assert round(analysis["average_record_size_in_bytes"]) == 12 if IS_UNIX else 14
    assert analysis["fields"] == 4
    assert analysis["field_stats"] == {}
    assert analysis["rows"] == 4
    assert analysis["rows_with_null_values"] == 3
    assert analysis["not_null_rows"] == 1
    assert analysis["variable_types"] == {}


def test_analyze_resource_detailed_with_invalid_data():
    resource = Resource({"path": "data/invalid.csv"})
    analysis = resource.analyze(detailed=True)
    assert round(analysis["average_record_size_in_bytes"]) == 12 if IS_UNIX else 14
    assert analysis["fields"] == 4
    assert list(analysis["field_stats"].keys()) == ["id", "name", "field3", "name2"]
    assert analysis["rows"] == 4
    assert analysis["rows_with_null_values"] == 3
    assert analysis["not_null_rows"] == 1
    assert analysis["variable_types"] == {"integer": 3, "string": 1}
