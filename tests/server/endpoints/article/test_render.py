# Action


def test_server_article_render(client):
    text = client("/article/render", text="**word**").text
    assert text == "<p><strong>word</strong></p>\n"
