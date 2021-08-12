import json
from ..type import Type

# retrieving type classes
valid_array_item_types = [
    'boolean', 
    'date', 
    'datetime', 
    'duration', 
    'geojson', 
    'geopoint', 
    'integer', 
    'number', 
    'object', 
    'string'
]

get_type_class = lambda type_: getattr(__import__(f'frictionless.types.{type_}', fromlist=[f'{type_.capitalize()}Type']), f'{type_.capitalize()}Type')

type_to_class = {
    array_item_type: get_type_class(array_item_type)
    for array_item_type
    in valid_array_item_types
}


class ArrayType(Type):
    """Array type implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless import types`

    """

    code = "array"
    builtin = True
    constraints = [
        "required",
        "minLength",
        "maxLength",
        "enum",
    ]
    default_separators = [
        '|',
        ',',
        ';'
    ]

    # Read

    def read_cell(self, cell, strip_trailing_whitespace=True):
        if not isinstance(cell, list):
            if hasattr(self.field, 'format'):
                cell = cell.split(self.field.format)
                
            elif any(sep in cell for sep in default_separators):
                for sep in default_separators: 
                    cell = cell.split(sep)
                    
            else:
                return None

        if strip_trailing_whitespace == True:
            cell = [elem.strip() for elem in cell]

        if hasattr(self.field, 'array_item'):
            if hasattr(self.field.array_item, 'type'):
                array_item_class = type_to_class[self.field.array_item.type]
                cell = [array_item_class().read_cell(cell_item) for cell_item in cell]

        return cell

    # Write

    def write_cell(self, cell):
        if hasattr(self.field, 'format'):
            cell = self.field.format.join(cell)

        else:
            cell = json.dumps(cell)

        return cell
