import sys

import pytest

from frictionless import platform
from frictionless.resources import TableResource

IS_UNIX = platform.type != "windows"

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 10),
    reason="Supported on Python3.10+",
)


# General


def test_analyze_resource():
    resource = TableResource(path="data/analysis-data.csv")
    analysis = resource.analyze()
    assert list(analysis.keys()) == [
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
    assert round(analysis["averageRecordSizeInBytes"]) == 85 if IS_UNIX else 86
    assert analysis["fields"] == 11
    assert analysis["rows"] == 9
    assert analysis["rowsWithNullValues"] == 2
    assert analysis["notNullRows"] == 7
    assert analysis["variableTypes"] == {}


def test_analyze_resource_detailed():
    resource = TableResource(path="data/analysis-data.csv")
    analysis = resource.analyze(detailed=True)
    assert list(analysis.keys()) == [
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
    assert round(analysis["averageRecordSizeInBytes"]) == 85 if IS_UNIX else 86
    assert analysis["fields"] == 11
    assert analysis["rows"] == 9
    assert analysis["rowsWithNullValues"] == 2
    assert analysis["notNullRows"] == 7
    assert analysis["variableTypes"] == {
        "boolean": 2,
        "integer": 2,
        "number": 2,
        "string": 5,
    }


def test_analyze_resource_detailed_non_numeric_values_summary():
    resource = TableResource(path="data/analysis-data.csv")
    analysis = resource.analyze(detailed=True)
    assert list(analysis["fieldStats"]["gender"].keys()) == ["type", "values"]


def test_analyze_resource_detailed_numeric_values_descriptive_summray():
    resource = TableResource(path="data/analysis-data.csv")
    analysis = resource.analyze(detailed=True)
    assert list(analysis["fieldStats"]["parent_age"].keys()) == [
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


def test_analyze_resource_detailed_numeric_descriptive_statistics():
    resource = TableResource(path="data/analysis-data.csv")
    analysis = resource.analyze(detailed=True)
    assert analysis["fieldStats"]["parent_age"]["bounds"] == [39, 67]
    assert analysis["fieldStats"]["parent_age"]["max"] == 57
    assert analysis["fieldStats"]["parent_age"]["mean"] == 52.666666666666664
    assert analysis["fieldStats"]["parent_age"]["median"] == 52
    assert analysis["fieldStats"]["parent_age"]["min"] == 48
    assert analysis["fieldStats"]["parent_age"]["missingValues"] == 0
    assert analysis["fieldStats"]["parent_age"]["mode"] == 57
    assert analysis["fieldStats"]["parent_age"]["quantiles"] == [49.5, 52.0, 56.5]
    assert analysis["fieldStats"]["parent_age"]["stdev"] == 3.391164991562634
    assert analysis["fieldStats"]["parent_age"]["uniqueValues"] == 7
    assert analysis["fieldStats"]["parent_age"]["variance"] == 11.5
    assert analysis["fieldStats"]["parent_age"]["outliers"] == []


def test_analyze_resource_detailed_numeric_descriptive_statistics_with_missingValues():
    resource = TableResource(path="data/analysis-data.csv")
    analysis = resource.analyze(detailed=True)
    assert analysis["fieldStats"]["average_grades"]["bounds"] == [81, 96]
    assert analysis["fieldStats"]["average_grades"]["max"] == 10000.0
    assert analysis["fieldStats"]["average_grades"]["mean"] == 1503.28
    assert analysis["fieldStats"]["average_grades"]["median"] == 86.91
    assert analysis["fieldStats"]["average_grades"]["min"] == 84.65
    assert analysis["fieldStats"]["average_grades"]["missingValues"] == 2
    assert analysis["fieldStats"]["average_grades"]["mode"] == 86.79
    assert analysis["fieldStats"]["average_grades"]["quantiles"] == [86.79, 86.91, 90.39]
    assert round(analysis["fieldStats"]["average_grades"]["stdev"]) == 3747
    assert analysis["fieldStats"]["average_grades"]["uniqueValues"] == 6
    assert round(analysis["fieldStats"]["average_grades"]["variance"]) == 14037774
    assert analysis["fieldStats"]["average_grades"]["outliers"] == [10000.0]


def test_analyze_resource_detailed_descriptive_statistics_with_outliers():
    resource = TableResource(path="data/analysis-data.csv")
    analysis = resource.analyze(detailed=True)
    assert analysis["fieldStats"]["average_grades"]["bounds"] == [81, 96]
    assert analysis["fieldStats"]["average_grades"]["outliers"] == [10000.0]


def test_analyze_resource_detailed_descriptive_statistics_variables_correlation():
    resource = TableResource(path="data/analysis-data.csv")
    analysis = resource.analyze(detailed=True)
    assert list(analysis["correlations"].keys()) == [
        "parent_age",
        "parent_salary",
        "house_area",
        "average_grades",
    ]
    assert (
        analysis["correlations"]["average_grades"][0]["fieldName"] == "parent_age"
        and analysis["correlations"]["average_grades"][0]["corr"] == -0.09401771232099933
    )
    assert (
        analysis["correlations"]["average_grades"][1]["fieldName"] == "parent_salary"
        and analysis["correlations"]["average_grades"][1]["corr"] == 0.4241304392492213
    )
    assert (
        analysis["correlations"]["average_grades"][2]["fieldName"] == "house_area"
        and analysis["correlations"]["average_grades"][2]["corr"] == 0.14354348594097088
    )
    assert (
        analysis["correlations"]["average_grades"][3]["fieldName"] == "average_grades"
        and analysis["correlations"]["average_grades"][3]["corr"] == 1.0
    )


def test_analyze_resource_detailed_non_numeric_summary():
    resource = TableResource(path="data/analysis-data.csv")
    analysis = resource.analyze(detailed=True)
    assert list(analysis["fieldStats"]["gender"].keys()) == ["type", "values"]
    assert analysis["fieldStats"]["gender"]["values"] == {"Male", "Female"}


def test_analyze_resource_detailed_non_numeric_data_identification():
    data = [
        ["gender", "country"],
        ["male", "usa"],
        ["female", "usa"],
        ["male", "italy"],
        ["female", "italy"],
        ["female", "italy"],
    ]
    resource = TableResource(data=data)
    analysis = resource.analyze(detailed=True)
    assert analysis["fieldStats"]["gender"]["type"] == "categorical"
    assert analysis["fieldStats"]["gender"]["values"] == {"male", "female"}
    assert analysis["fieldStats"]["country"]["type"] == "categorical"
    assert analysis["fieldStats"]["country"]["values"] == {"usa", "italy"}


def test_analyze_resource_with_empty_rows():
    data = [["a", "b"]]
    resource = TableResource(data=data)
    analysis = resource.analyze()
    assert list(analysis.keys()) == [
        "variableTypes",
        "notNullRows",
        "rowsWithNullValues",
        "fieldStats",
        "averageRecordSizeInBytes",
        "timeTaken",
        "fields",
        "rows",
    ]
    assert analysis["rows"] == 0


def test_analyze_resource_detailed_with_empty_rows():
    data = [["a", "b"]]
    resource = TableResource(data=data)
    analysis = resource.analyze(detailed=True)
    assert list(analysis.keys()) == [
        "variableTypes",
        "notNullRows",
        "rowsWithNullValues",
        "fieldStats",
        "averageRecordSizeInBytes",
        "timeTaken",
        "fields",
        "rows",
    ]
    assert analysis["rows"] == 0


def test_analyze_resource_with_invalid_data():
    resource = TableResource(path="data/invalid.csv")
    analysis = resource.analyze()
    assert round(analysis["averageRecordSizeInBytes"]) == 12 if IS_UNIX else 14
    assert analysis["fields"] == 4
    assert analysis["fieldStats"] == {}
    assert analysis["rows"] == 4
    assert analysis["rowsWithNullValues"] == 3
    assert analysis["notNullRows"] == 1
    assert analysis["variableTypes"] == {}


def test_analyze_resource_detailed_with_invalid_data():
    resource = TableResource(path="data/invalid.csv")
    analysis = resource.analyze(detailed=True)
    assert round(analysis["averageRecordSizeInBytes"]) == 12 if IS_UNIX else 14
    assert analysis["fields"] == 4
    assert list(analysis["fieldStats"].keys()) == ["id", "name", "field3", "name2"]
    assert analysis["rows"] == 4
    assert analysis["rowsWithNullValues"] == 3
    assert analysis["notNullRows"] == 1
    assert analysis["variableTypes"] == {"integer": 3, "string": 1}
