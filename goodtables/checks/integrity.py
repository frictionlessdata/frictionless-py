from .. import errors
from .. import helpers
from ..check import Check


class IntegrityCheck(Check):
    metadata_profile = {  # type: ignore
        'type': 'object',
        'properties': {
            'size': {'type': ['number', 'null']},
            'hash': {'type': ['string', 'null']},
            'lookup': {'type': ['object', 'null']},
        },
    }
    possible_Errors = [  # type: ignore
        # table
        errors.SizeError,
        errors.HashError,
        # body
        errors.UniqueError,
        errors.PrimaryKeyError,
        errors.ForeignKeyError,
    ]

    def prepare(self):
        self.size = self.get('size')
        self.hash = self.get('hash')
        self.lookup = self.get('lookup')
        self.memory_unique = {}
        for field in self.schema.fields:
            if field.constraints.get('unique'):
                self.memory_unique[field.name] = {}
        self.memory_primary = {}
        self.foreign_groups = []
        if self.lookup:
            for fk in self.schema.foreign_keys:
                group = {}
                group['sourceName'] = fk['reference']['resource']
                group['sourceKey'] = tuple(fk['reference']['fields'])
                group['targetKey'] = tuple(fk['fields'])
                self.foreign_groups.append(group)

    # Validate

    def validate_row(self, row):

        # Unique Error
        if self.memory_unique:
            for field_name in self.memory_unique.keys():
                cell = row[field_name]
                if cell is not None:
                    match = self.memory_unique[field_name].get(cell)
                    self.memory_unique[field_name][cell] = row.row_position
                    if match:
                        note = 'the same as in the row at position %s' % match
                        yield errors.UniqueError.from_row(
                            row, note=note, field_name=field_name
                        )

        # Primary Key Error
        if self.schema.primary_key:
            cells = tuple(row[field_name] for field_name in self.schema.primary_key)
            if set(cells) == {None}:
                note = 'cells composing the primary keys are all "None"'
                yield errors.PrimaryKeyError.from_row(row, note=note)
            else:
                match = self.memory_primary.get(cells)
                self.memory_primary[cells] = row.row_position
                if match:
                    if match:
                        note = 'the same as in the row at position %s' % match
                        yield errors.PrimaryKeyError.from_row(row, note=note)

        # Foreign Key Error
        if self.foreign_groups:
            for group in self.foreign_groups:
                group_lookup = self.lookup.get(group['sourceName'])
                if group_lookup:
                    cells = tuple(row[field_name] for field_name in group['targetKey'])
                    if set(cells) == {None}:
                        continue
                    match = cells in group_lookup.get(group['sourceKey'], set())
                    if not match:
                        note = 'not found in the lookup table'
                        yield errors.ForeignKeyError.from_row(row, note=note)

    def validate_table(self):

        # Size error
        if self.size:
            if self.size != self.stream.size:
                note = 'expected is "%s" and actual is "%s"'
                note = note % (self.size, self.stream.size)
                yield errors.SizeError(note=note)

        # Hash error
        if self.hash:
            hashing_digest = helpers.parse_hashing_digest(self.hash)
            if hashing_digest != self.stream.hash:
                note = 'expected is "%s" and actual is "%s"'
                note = note % (hashing_digest, self.stream.hash)
                yield errors.HashError(note=note)
