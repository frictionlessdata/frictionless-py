# Action


def test_server_text_render(client):
    text = client("/text/render", text="**word**").text
    assert text == "<p><strong>word</strong></p>\n"
