from __future__ import annotations

from typing import Dict, List, Optional, Set

from ..schema import Field


def deduplicate_names(names: List[str]) -> List[str]:
    """Renames the duplicated names so that every name is unique.

    The first occurrence keeps its name; a later duplicate becomes the first
    free name among `{name}2`, `{name}3`, etc. Names are compared
    case-sensitively, matching the schema validity rule (fields differing
    only by case are distinct).
    """
    result: List[str] = []
    used_names: Set[str] = set()
    for name in names:
        new_name = name
        suffix = 2
        while new_name in used_names:
            new_name = f"{name}{suffix}"
            suffix += 1
        result.append(new_name)
        used_names.add(new_name)
    return result


class LabelMatching:
    """Pairs the labels read from the data source with the schema fields, by name.

    Parameters:
        labels (str[]): the header row as read from the data source
        fields (Field[]): the fields declared in the schema, in schema order
        ignore_case (bool): compare labels and field names case-insensitively
    """

    def __init__(
        self,
        labels: List[str],
        fields: List[Field],
        *,
        ignore_case: bool = False,
    ) -> None:
        self.__labels = labels
        self.__fields = fields
        self.__ignore_case = ignore_case

        # Keyed by normalized name, in schema order; the first field wins in
        # case of duplicates under normalization, so the duplicate fields are
        # lost
        fields_by_key: Dict[str, Field] = {}
        for field in fields:
            fields_by_key.setdefault(self.__normalize(field.name), field)

        self.__fields_by_key = fields_by_key

    def matching_field(self, label: str) -> Optional[Field]:
        """Returns the field the given label matches, or None if there is none"""
        return self.__fields_by_key.get(self.__normalize(label))

    def matches(self, label: str, field: Field) -> bool:
        """Whether the given label and field designate the same column

        Unlike `matching_field`, which searches the whole schema, this answers
        for one given pair -- what the positional modes need, since there the
        pairing comes from the order rather than from the names.
        """
        return self.__normalize(label) == self.__normalize(field.name)

    @property
    def unmatched_fields(self) -> List[Field]:
        """The fields no label matches, in schema order"""
        matched = {self.__normalize(label) for label in self.__labels}
        return [
            field
            for field in self.__fields
            if self.__normalize(field.name) not in matched
        ]

    @property
    def ambiguous_fields(self) -> List[List[Field]]:
        """Groups of fields that normalization merges into a single key

        Fields sharing the very same name make the schema itself invalid, which is caught
        before a header is ever built.
        """
        groups: Dict[str, List[Field]] = {}
        for field in self.__fields:
            groups.setdefault(self.__normalize(field.name), []).append(field)
        return [
            group for group in groups.values() if len({field.name for field in group}) > 1
        ]

    @property
    def has_duplicate_labels(self) -> bool:
        """Whether two labels match the same field, which makes the mapping ambiguous

        Labels are compared the way they are matched, so under `ignore_case`
        two labels differing only by case are duplicates.
        """
        keys = [self.__normalize(label) for label in self.__labels]
        return len(keys) != len(set(keys))

    @property
    def has_match(self) -> bool:
        """Whether at least one label matches a schema field"""
        return any(self.matching_field(label) is not None for label in self.__labels)

    def __normalize(self, name: str) -> str:
        """The normalized value a label and a field name are compared through"""
        return name.lower() if self.__ignore_case else name
