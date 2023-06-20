from frictionless.resources import ArticleResource

# General


def test_resource_render_article():
    resource = ArticleResource(path="data/article.md")
    assert resource.render_article().count("<h1>Article</h1>\n<p>Contents</p>\n")
