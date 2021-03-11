from .table import TableError


class HeaderError(TableError):
    """Header error representation

    Parameters:
        descriptor? (str|dict): error descriptor
        note (str): an error note
        labels (str[]): header labels
        label (str): an errored label
        field_name (str): field name
        field_number (int): field number
        field_position (int): field position

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    code = "header-error"
    name = "Header Error"
    tags = ["#table", "#header"]
    template = "Cell Error"
    description = "Cell Error"

    def __init__(
        self,
        descriptor=None,
        *,
        note,
        labels,
        row_positions,
    ):
        self.setinitial("labels", labels)
        self.setinitial("rowPositions", row_positions)
        super().__init__(descriptor, note=note)


class BlankHeaderError(HeaderError):
    code = "blank-header"
    name = "Blank Header"
    template = "Header is completely blank"
    description = "This header is empty. A header should contain at least one value."
