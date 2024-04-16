import pytest

from frictionless import platform
from frictionless.resources import FileResource

# General


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_read_file():
    resource = FileResource(path="data/article.md")
    assert resource.read_file() == b"# Article\n\nContents\n"


def test_resource_read_file_from_data():
    resource = FileResource(data=b"my file")
    assert resource.read_file() == b"my file"
