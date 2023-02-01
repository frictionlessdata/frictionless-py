from frictionless import Project


name1 = "name1.txt"
name2 = "name2.txt"
bytes1 = b"bytes1"
bytes2 = b"bytes2"
bytes3 = b'{"key": "value"}'
folder1 = "folder1"
folder2 = "folder2"


# Create


def test_project_folder_create(tmpdir):
    project = Project(basepath=tmpdir, is_root=True)
    path = project.folder_create(folder1)
    assert path == folder1
    assert project.file_list() == [
        {"path": folder1, "type": "folder"},
    ]
