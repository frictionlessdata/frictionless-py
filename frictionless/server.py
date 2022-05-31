class Server:
    """Server representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Schema`

    """

    def start(self, port: int) -> None:
        """Start the server

        Parameters:
            port (int): HTTP port
        """
        raise NotImplementedError()

    def stop(self) -> None:
        """Stop the server"""
        raise NotImplementedError()
