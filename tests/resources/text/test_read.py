from frictionless.resources import TextResource

# General


def test_resource_read_text():
    resource = TextResource(path="data/article.md")
    assert resource.read_text() == "# Article\n\nContents\n"


def test_resource_read_text_from_data():
    resource = TextResource(data="my text")
    assert resource.read_text() == "my text"
