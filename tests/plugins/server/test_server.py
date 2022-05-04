from frictionless import system


# General


def test_server_api():
    server = system.create_server("api")
    assert server.start
    assert server.stop
