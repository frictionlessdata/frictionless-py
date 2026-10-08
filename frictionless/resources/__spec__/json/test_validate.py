import pytest

from frictionless.resources import (
    ChartResource,
    JsonResource,
    JsonschemaResource,
    MapResource,
    ViewResource,
)


@pytest.mark.parametrize(
    "resource_class, filename",
    [
        (JsonResource, "data.json"),
        (ChartResource, "chart.json"),
        (JsonschemaResource, "schema.json"),
        (MapResource, "map.json"),
        (ViewResource, "view.json"),
    ],
)
def test_json_resource_validate_invalid_json(resource_class, filename, tmpdir):
    path = tmpdir.join(filename)
    path.write('{"broken": true "comma": false}')

    report = resource_class(path=filename, basepath=str(tmpdir)).validate()

    assert not report.valid
    assert report.flatten(["type"]) == [["format-error"]]


@pytest.mark.parametrize("filename", ["data.json", "data.yaml"])
def test_json_resource_validate_valid_document(filename, tmpdir):
    path = tmpdir.join(filename)
    path.write('{"valid": true}')

    report = JsonResource(path=filename, basepath=str(tmpdir)).validate()

    assert report.valid
