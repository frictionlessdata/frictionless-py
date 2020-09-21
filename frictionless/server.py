class Server:
    """Server representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Schema`

    """

    def start(self, port):
        """Start the server

        Parameters:
            port (int): HTTP port
        """
        raise NotImplementedError()

    def stop(self):
        """Stop the server"""
        raise NotImplementedError()
