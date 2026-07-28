from __future__ import annotations

from typing import Dict, List, Optional

from ..schema import Field


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
    def has_match(self) -> bool:
        """Whether at least one label matches a schema field"""
        return any(self.matching_field(label) is not None for label in self.__labels)

    def __normalize(self, name: str) -> str:
        """The normalized value a label and a field name are compared through"""
        return name.lower() if self.__ignore_case else name
