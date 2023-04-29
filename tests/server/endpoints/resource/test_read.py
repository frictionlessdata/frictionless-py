# Select


#  def test_project_select_file(tmpdir):
#  project = Project(tmpdir)
#  project.upload_file(name1, bytes=bytes1)
#  assert project.select_file(name1) == {"path": name1, "type": "text"}
#  assert project.list_files() == [
#  {"path": name1, "type": "text"},
#  ]


#  @pytest.mark.parametrize("path", not_secure)
#  def test_project_select_file_security(tmpdir, path):
#  project = Project(tmpdir)
#  with pytest.raises(Exception):
#  project.select_file(path)
