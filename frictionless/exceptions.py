class FrictionlessException(Exception):
    """Main Frictionless exception

    API      | Usage
    -------- | --------
    Public   | `from frictionless import exceptions`

    Parameters:
        error (Error): an underlaying error

    """

    def __init__(self, error):
        self.__error = error
        super().__init__(f"[{error.code}] {error.message}")

    @property
    def error(self):
        """
        Returns:
            Error: error
        """
        return self.__error
