import json

from frictionless import Package, Resource, Schema, formats
from frictionless.console import console
from frictionless.console.commands.__spec__.conftest import create_runner
from frictionless.resources import PackageResource, TableResource

runner = create_runner()

POINTS_FIELDS = [
    {"name": "id", "type": "integer"},
    {"name": "name", "type": "string"},
    {"name": "height", "type": "number"},
    {"name": "built", "type": "string"},
    {"name": "geometry", "type": "string", "format": "wkt"},
]
POINTS_ROWS = [
    {
        "id": 1,
        "name": "english",
        "height": 1.5,
        "built": "2020/01/31 00:00:00",
        "geometry": "POINT (10 53.5)",
    },
    {
        "id": 2,
        "name": "Straßenkreuzung",
        "height": 2.25,
        "built": None,
        "geometry": None,
    },
]
AREAS_ROWS = [{"code": "A1", "geometry": "POLYGON ((0 0, 1 1, 1 0, 0 0))"}]


# Read


def test_shapefile_parser():
    with TableResource(path="data/shapefile/points.shp") as resource:
        assert resource.format == "shp"
        assert resource.schema.to_descriptor() == {"fields": POINTS_FIELDS}
        assert resource.read_rows() == POINTS_ROWS


def test_shapefile_parser_zip():
    resource = Resource("data/shapefile/points.zip")
    assert isinstance(resource, TableResource)
    assert resource.format == "shp"
    assert resource.compression is None
    assert resource.read_rows() == POINTS_ROWS


def test_shapefile_parser_zip_layer():
    control = formats.ShapefileControl(layer="areas")
    resource = Resource("data/shapefile/layers.zip", control=control)
    assert isinstance(resource, TableResource)
    assert resource.read_rows() == AREAS_ROWS


def test_shapefile_parser_zip_innerpath():
    resource = TableResource(path="data/shapefile/layers.zip", innerpath="areas.shp")
    assert resource.read_rows() == AREAS_ROWS


def test_shapefile_parser_zip_multiple_layers():
    resource = Resource("data/shapefile/layers.zip")
    assert isinstance(resource, PackageResource)
    package = resource.read_metadata()
    assert package.resource_names == ["points", "areas"]


def test_shapefile_package():
    package = Package("data/shapefile/layers.zip")
    assert package.resource_names == ["points", "areas"]
    areas = package.get_table_resource("areas")
    assert areas.dialect.to_descriptor() == {"shapefile": {"layer": "areas"}}
    assert areas.read_rows() == AREAS_ROWS
    assert package.validate().valid


def test_shapefile_parser_refined_schema():
    schema = Schema.from_descriptor("data/shapefile/points.schema.yaml")
    resource = TableResource(path="data/shapefile/points.zip", schema=schema)
    report = resource.validate()
    assert report.flatten(["rowNumber", "fieldNumber", "type"]) == [
        [3, 3, "constraint-error"],
        [3, 5, "constraint-error"],
    ]


def test_shapefile_zip_package_is_not_shapefile():
    package = Package("data/package.zip")
    assert "shapefile" not in package.resources[0].dialect.to_descriptor()


# Console


def test_shapefile_console_describe():
    actual = runner.invoke(console, "describe data/shapefile/points.zip --json")
    assert actual.exit_code == 0
    descriptor = json.loads(actual.stdout)
    assert descriptor["format"] == "shp"
    assert descriptor["schema"] == {"fields": POINTS_FIELDS}


def test_shapefile_console_describe_multiple_layers():
    actual = runner.invoke(console, "describe data/shapefile/layers.zip --json")
    assert actual.exit_code == 0
    descriptor = json.loads(actual.stdout)
    assert [res["name"] for res in descriptor["resources"]] == ["points", "areas"]


def test_shapefile_console_extract():
    actual = runner.invoke(console, "extract data/shapefile/layers.zip --json")
    assert actual.exit_code == 0
    assert json.loads(actual.stdout) == {
        "points": [{**row, "height": str(row["height"])} for row in POINTS_ROWS],
        "areas": AREAS_ROWS,
    }


def test_shapefile_console_validate():
    actual = runner.invoke(console, "validate data/shapefile/layers.zip")
    assert actual.exit_code == 0
    assert actual.stdout.count("VALID") == 2


def test_shapefile_console_validate_refined_schema():
    command = "validate data/shapefile/points.zip --schema data/shapefile/points.schema.yaml --json"
    actual = runner.invoke(console, command)
    assert actual.exit_code == 1
    report = json.loads(actual.stdout)
    errors = report["tasks"][0]["errors"]
    assert [(error["rowNumber"], error["fieldName"]) for error in errors] == [
        (3, "height"),
        (3, "geometry"),
    ]
