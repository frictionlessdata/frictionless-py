from frictionless.resources import TextResource

# General


def test_resource_write_text(tmpdir):
    source = TextResource(path="data/article.md")
    target = source.write_text(path=str(tmpdir.join("article.md")))
    assert target.read_text() == "# Article\n\nContents\n"
