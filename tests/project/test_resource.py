from frictionless import Project, Resource


dir1 = "dir1"
dir2 = "dir2"
name1 = "name1.csv"
name2 = "name2.txt"
bytes1 = b"id,name\n1,english\n2,spanish"
bytes2 = b"bytes1"


# Read


def test_project_resource_create(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.file_create(name1, bytes=bytes1)
    item = project.resource_create(name1)
    data = project.resource_query("SELECT * FROM name1")
    resource = Resource.from_descriptor(item["resource"])
    assert item["path"] == name1
    assert item["updated"]
    assert item["tableName"] == "name1"
    assert resource.path == name1
    assert resource.schema.field_names == ["id", "name"]
    assert resource.schema.field_types == ["integer", "string"]
    assert data == [
        {"_rowNumber": 2, "_rowValid": True, "id": 1, "name": "english"},
        {"_rowNumber": 3, "_rowValid": True, "id": 2, "name": "spanish"},
    ]
