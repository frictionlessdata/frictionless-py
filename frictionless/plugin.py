class Plugin:
    """Plugin representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Plugin`

    It's an interface for writing Frictionless plugins.
    You can implement one or more methods to hook into Frictionless system.

    """

    code = "plugin"
    status = "stable"

    def create_candidates(self, candidates):
        """Create candidates

        Returns:
            dict[]: an ordered by priority list of type descriptors for type detection
        """
        pass

    def create_check(self, name, *, descriptor=None):
        """Create check

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

    def create_error(self, descriptor):
        """Create error

        Parameters:
            descriptor (dict): error descriptor

        Returns:
            Error: error
        """
        pass

    def create_file(self, source, **options):
        """Create file

        Parameters:
            source (any): file source
            options (dict): file options

        Returns:
            File: file
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

    def create_step(self, descriptor):
        """Create step

        Parameters:
            descriptor (dict): step descriptor

        Returns:
            Step: step
        """
        pass

    def create_storage(self, name, source, **options):
        """Create storage

        Parameters:
            name (str): storage name
            options (str): storage options

        Returns:
            Storage: storage
        """
        pass

    def create_type(self, field):
        """Create type

        Parameters:
            field (Field): corresponding field

        Returns:
            Type: type
        """
        pass
