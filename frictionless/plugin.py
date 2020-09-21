class Plugin:
    """Plugin representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Plugin`

    It's an interface for writing Frictionless plugins.
    You can implement one or more methods to hook into Frictionless system.

    """

    def create_check(self, name, *, descriptor=None):
        """Create checks

        Parameters:
            name (str): check name
            descriptor (dict): check descriptor

        Returns:
            Check: check
        """
        pass

    def create_control(self, file, *, descriptor):
        """Create control

        Parameters:
            file (File): control file
            descriptor (dict): control descriptor

        Returns:
            Control: control
        """
        pass

    def create_dialect(self, file, *, descriptor):
        """Create dialect

        Parameters:
            file (File): dialect file
            descriptor (dict): dialect descriptor

        Returns:
            Dialect: dialect
        """
        pass

    def create_loader(self, file):
        """Create loader

        Parameters:
            file (File): loader file

        Returns:
            Loader: loader
        """
        pass

    def create_parser(self, file):
        """Create parser

        Parameters:
            file (File): parser file

        Returns:
            Parser: parser
        """
        pass

    def create_server(self, name):
        """Create server

        Parameters:
            name (str): server name

        Returns:
            Server: server
        """
        pass
