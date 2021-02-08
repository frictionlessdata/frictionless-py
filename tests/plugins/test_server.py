from frictionless import system


# API


def test_server_api():
    server = system.create_server("api")
    assert server.start
    assert server.stop
