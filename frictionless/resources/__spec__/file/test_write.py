import pytest

from frictionless import platform
from frictionless.resources import FileResource

# General


@pytest.mark.skipif(platform.type == "windows", reason="Fix on Windows")
def test_resource_write_text(tmpdir):
    source = FileResource(path="data/article.md")
    target = source.write_file(path=str(tmpdir.join("article.md")))
    assert target.read_file() == b"# Article\n\nContents\n"
