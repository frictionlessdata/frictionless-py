from frictionless.resources import TextResource


# General


def test_resource_read_text():
    resource = TextResource(path="data/article.md")
    assert resource.read_text() == "# Article\n\nContents\n"
