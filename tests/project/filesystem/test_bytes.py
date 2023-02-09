import pytest
from frictionless import Filesystem


name1 = "name1.txt"
name2 = "name2.txt"
bytes1 = b"bytes1"
bytes2 = b"bytes2"
bytes3 = b'{"key": "value"}'
folder1 = "folder1"
folder2 = "folder2"
not_secure = ["/path", "../path", "../", "./"]


# Read


def test_filesystem_read_file_bytes(tmpdir):
    fs = Filesystem(tmpdir)
    fs.create_file(name1, bytes=bytes1)
    assert fs.read_bytes(name1) == bytes1
    assert fs.list_files() == [
        {"path": name1, "type": "file"},
    ]


@pytest.mark.parametrize("path", not_secure)
def test_filesystem_read_file_bytes_security(tmpdir, path):
    fs = Filesystem(tmpdir)
    with pytest.raises(Exception):
        fs.read_bytes(path)
