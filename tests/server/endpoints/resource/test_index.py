#  def test_project_index_file(tmpdir):
#  project = Project(tmpdir)
#  path = project.upload_file(name4, bytes=bytes4)
#  file = project.index_file(path)
#  assert file
#  assert file["path"] == name4
#  assert file.get("type") == "table"
#  record = file.get("record")
#  table = project.query_table("SELECT * FROM name4")
#  assert record
#  assert record["updated"]
#  assert record.get("tableName") == "name4"
#  assert record["resource"]["path"] == name4
#  assert record["resource"]["schema"]["fields"][0] == dict(name="id", type="integer")
#  assert record["resource"]["schema"]["fields"][0] == dict(name="id", type="integer")
#  assert record["resource"]["schema"]["fields"][1] == dict(name="name", type="string")
#  assert table["tableSchema"]
#  assert table["header"] == ["_rowNumber", "_rowValid", "id", "name"]
#  assert table["rows"] == [
#  {"_rowNumber": 2, "_rowValid": True, "id": 1, "name": "english"},
#  {"_rowNumber": 3, "_rowValid": True, "id": 2, "name": "spanish"},
#  ]
