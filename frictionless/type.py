from .helpers import cached_property


class Type:
    """Data type representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Type`

    This class is for subclassing.

    Parameters:
        field (Field): field
    """

    code = "type"
    constraints = []
    """
    Returns:
        str[]: a list of supported constraints
    """

    def __init__(self, field):
        self.__field = field

    @cached_property
    def field(self):
        """
        Returns:
            Field: field
        """
        return self.__field

    # Read

    def read_cell(self, cell):
        """Convert cell (read direction)

        Parameters:
            cell (any): cell to covert

        Returns:
            any: converted cell
        """
        raise NotImplementedError()

    # Write

    def write_cell(self, cell):
        """Convert cell (write direction)

        Parameters:
            cell (any): cell to covert

        Returns:
            any: converted cell
        """
        raise NotImplementedError()
