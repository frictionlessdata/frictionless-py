from frictionless import Project


dir1 = "dir1"
dir2 = "dir2"
name1 = "name1.csv"
name2 = "name2.txt"
bytes1 = b"id,name\n1,english\n2,spanish"
bytes2 = b"bytes1"


# Read


def test_project_resource_create(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    project.create_file(name1, bytes=bytes1)
    record = project.create_resource(name1)
    table = project.query_resources("SELECT * FROM name1")
    assert record["path"] == name1
    assert record["type"] == "table"
    assert record["updated"]
    assert record["tableName"] == "name1"
    assert record["resource"]["path"] == name1
    assert record["resource"]["schema"]["fields"][0] == dict(name="id", type="integer")
    assert record["resource"]["schema"]["fields"][0] == dict(name="id", type="integer")
    assert record["resource"]["schema"]["fields"][1] == dict(name="name", type="string")
    assert table["tableSchema"]
    assert table["header"] == ["_rowNumber", "_rowValid", "id", "name"]
    assert table["rows"] == [
        {"_rowNumber": 2, "_rowValid": True, "id": 1, "name": "english"},
        {"_rowNumber": 3, "_rowValid": True, "id": 2, "name": "spanish"},
    ]
