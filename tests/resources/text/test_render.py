from frictionless.resources import TextResource


# General


def test_resource_read_text():
    resource = TextResource(path="data/article.md")
    assert resource.render_text().count("<h1>Article</h1>\n<p>Contents</p>\n")
