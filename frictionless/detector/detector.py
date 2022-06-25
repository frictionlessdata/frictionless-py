from __future__ import annotations
import codecs
import chardet
from copy import copy, deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, List
from ..metadata2 import Metadata2
from ..exception import FrictionlessException
from ..dialect import Dialect
from ..schema import Schema
from ..field import Field
from ..system import system
from .validate import validate
from .. import settings
from .. import errors

if TYPE_CHECKING:
    from ..interfaces import IBuffer, EncodingFunction
    from ..resource import Resource


@dataclass
class Detector(Metadata2):
    """Detector representation"""

    validate = validate

    # Properties

    buffer_size: int = settings.DEFAULT_BUFFER_SIZE
    """
    The amount of bytes to be extracted as a buffer.
    It defaults to 10000
    """

    sample_size: int = settings.DEFAULT_SAMPLE_SIZE
    """
    The amount of rows to be extracted as a sample.
    It defaults to 100
    """

    encoding_function: Optional[EncodingFunction] = None
    """
    A custom encoding function for the file.
    """

    encoding_confidence: float = settings.DEFAULT_ENCODING_CONFIDENCE
    """
    Confidence value for encoding function.
    """

    field_type: Optional[str] = None
    """
    Enforce all the inferred types to be this type.
    For more information, please check "Describing  Data" guide.
    """

    field_names: Optional[List[str]] = None
    """
    Enforce all the inferred fields to have provided names.
    For more information, please check "Describing  Data" guide.
    """

    field_confidence: float = settings.DEFAULT_FIELD_CONFIDENCE
    """
    A number from 0 to 1 setting the infer confidence.
    If  1 the data is guaranteed to be valid against the inferred schema.
    For more information, please check "Describing  Data" guide.
    It defaults to 0.9
    """

    field_float_numbers: bool = settings.DEFAULT_FLOAT_NUMBERS
    """
    Flag to indicate desired number type.
    By default numbers will be `Decimal`; if `True` - `float`.
    For more information, please check "Describing  Data" guide.
    It defaults to `False`
    """

    field_missing_values: List[str] = field(
        default_factory=settings.DEFAULT_MISSING_VALUES.copy
    )
    """
    String to be considered as missing values.
    For more information, please check "Describing  Data" guide.
    It defaults to `['']`
    """

    field_true_values: List[str] = field(
        default_factory=settings.DEFAULT_TRUE_VALUES.copy
    )
    """
    String to be considered as true values.
    For more information, please check "Describing  Data" guide.
    It defaults to `["true", "True", "TRUE", "1"]`
    """

    field_false_values: List[str] = field(
        default_factory=settings.DEFAULT_FALSE_VALUES.copy
    )
    """
    String to be considered as false values.
    For more information, please check "Describing  Data" guide.
    It defaults to `["false", "False", "FALSE", "0"]`
    """

    schema_sync: bool = False
    """
    Whether to sync the schema.
    If it sets to `True` the provided schema will be mapped to
    the inferred schema. It means that, for example, you can
    provide a subset of fileds to be applied on top of the inferred
    fields or the provided schema can have different order of fields.
    """

    schema_patch: Optional[dict] = None
    """
    A dictionary to be used as an inferred schema patch.
    The form of this dictionary should follow the Schema descriptor form
    except for the `fields` property which should be a mapping with the
    key named after a field name and the values being a field patch.
    For more information, please check "Extracting Data" guide.
    """

    # Detect

    def detect_encoding(self, buffer: IBuffer, *, encoding: Optional[str] = None):
        """Detect encoding from buffer

        Parameters:
            buffer (byte): byte buffer

        Returns:
            str: encoding
        """

        # User defined
        if self.encoding_function:
            return self.encoding_function(buffer)

        # Detect encoding
        if not encoding:
            detector = chardet.UniversalDetector()
            for line in buffer.splitlines():
                detector.feed(line)
            detector.close()
            encoding = detector.result["encoding"] or settings.DEFAULT_ENCODING
            confidence = detector.result["confidence"] or 0
            if confidence < self.encoding_confidence:
                encoding = settings.DEFAULT_ENCODING
            if encoding == "ascii":
                encoding = settings.DEFAULT_ENCODING

        # Normalize encoding
        encoding = codecs.lookup(encoding).name
        # Work around for incorrect inferion of utf-8-sig encoding
        if encoding == "utf-8":
            if buffer.startswith(codecs.BOM_UTF8):
                encoding = "utf-8-sig"
        # Use the BOM stripping name (without byte-order) for UTF-16 encodings
        elif encoding == "utf-16-be":
            if buffer.startswith(codecs.BOM_UTF16_BE):
                encoding = "utf-16"
        elif encoding == "utf-16-le":
            if buffer.startswith(codecs.BOM_UTF16_LE):
                encoding = "utf-16"

        return encoding

    def detect_dialect(self, sample, *, dialect: Optional[Dialect] = None) -> Dialect:
        """Detect dialect from sample

        Parameters:
            sample (any[][]): data sample
            dialect? (Dialect): file dialect

        Returns:
            Dialect: dialect
        """
        dialect = dialect or Dialect()
        comment_filter = dialect.create_comment_filter()

        # Infer header
        widths = [len(cells) for cells in sample]
        if (
            widths
            and not dialect.has_defined("header")
            and not dialect.has_defined("header_rows")
        ):

            # This algorithm tries to find a header row
            # that is close to average sample width or use default one
            # We use it to eleminate initial rows that are comments/etc

            # Get header rows
            width = round(sum(widths) / len(widths))
            drift = max(round(width * 0.1), 1)
            match = list(range(width - drift, width + drift + 1))
            header_rows = settings.DEFAULT_HEADER_ROWS.copy()
            for row_number, cells in enumerate(sample, start=1):
                if comment_filter:
                    if not comment_filter(row_number, cells):
                        continue
                if len(cells) in match:
                    header_rows = [row_number]
                    break

            # Set header rows
            if not header_rows:
                dialect.header = False
            elif header_rows != settings.DEFAULT_HEADER_ROWS:
                dialect.header_rows = header_rows
        return dialect

    def detect_schema(self, fragment, *, labels=None, schema=None):
        """Detect schema from fragment

        Parameters:
            fragment (any[][]): data fragment
            labels? (str[]): data labels
            schema? (Schema): data schema

        Returns:
            Schema: schema
        """

        # Create schema
        if not schema or not schema.fields:
            schema = Schema()

            # Missing values
            if self.field_missing_values != settings.DEFAULT_MISSING_VALUES:
                schema.missing_values = self.field_missing_values  # type: ignore

            # Prepare names
            names = copy(self.field_names or labels or [])
            names = list(map(lambda cell: cell.replace("\n", " ").strip(), names))
            if not names:
                if not fragment:
                    return schema
                names = [f"field{number}" for number in range(1, len(fragment[0]) + 1)]

            # Handle name/empty
            for index, name in enumerate(names):
                names[index] = name or f"field{index+1}"

            # Deduplicate names
            if len(names) != len(set(names)):
                seen_names = []
                names = names.copy()
                for index, name in enumerate(names):
                    count = seen_names.count(name) + 1
                    names[index] = "%s%s" % (name, count) if count > 1 else name
                    seen_names.append(name)

            # Handle type/empty
            if self.field_type or not fragment:
                type = self.field_type
                schema.fields = [{"name": name, "type": type or "any"} for name in names]  # type: ignore
                return schema

            # Prepare runners
            runners = []
            runner_fields = []  # we use shared fields
            for candidate in system.create_field_candidates():
                field = Field(candidate)
                if field.type == "number" and self.field_float_numbers:
                    field.float_number = True  # type: ignore
                elif field.type == "boolean":
                    if self.field_true_values != settings.DEFAULT_TRUE_VALUES:
                        field.true_values = self.field_true_values  # type: ignore
                    if self.field_false_values != settings.DEFAULT_FALSE_VALUES:
                        field.false_values = self.field_false_values  # type: ignore
                runner_fields.append(field)
            for index, name in enumerate(names):
                runners.append([])
                for field in runner_fields:
                    runners[index].append({"field": field, "score": 0})

            # Infer fields
            fields = [None] * len(names)
            max_score = [len(fragment)] * len(names)
            threshold = len(fragment) * (self.field_confidence - 1)
            for cells in fragment:
                for index, name in enumerate(names):
                    if fields[index] is not None:
                        continue
                    source = cells[index] if len(cells) > index else None
                    is_field_missing_value = source in self.field_missing_values
                    if is_field_missing_value:
                        max_score[index] -= 1
                    for runner in runners[index]:
                        if runner["score"] < threshold:
                            continue
                        if not is_field_missing_value:
                            _, notes = runner["field"].read_cell(source)
                            runner["score"] += 1 if not notes else -1
                        if max_score[index] > 0 and runner["score"] >= (
                            max_score[index] * self.field_confidence
                        ):
                            field = runner["field"].to_copy()
                            field.name = name
                            field.schema = schema
                            fields[index] = field
                            break

            # Fill/set fields
            # For not inferred fields we use the "any" type field as a default
            for index, name in enumerate(names):
                if fields[index] is None:
                    fields[index] = Field(name=name, type="any", schema=schema)  # type: ignore
            schema.fields = fields  # type: ignore

        # Sync schema
        if self.schema_sync:
            if labels:
                fields = []
                mapping = {field.get("name"): field for field in schema.fields}  # type: ignore
                for name in labels:
                    fields.append(mapping.get(name, {"name": name, "type": "any"}))
                schema.fields = fields  # type: ignore

        # Patch schema
        if self.schema_patch:
            schema_patch = deepcopy(self.schema_patch)
            fields = schema_patch.pop("fields", {})
            schema.update(schema_patch)
            for field in schema.fields:  # type: ignore
                field.update((fields.get(field.get("name"), {})))

        # Validate schema
        # NOTE: at some point we might need to remove it for transform needs
        if len(schema.field_names) != len(set(schema.field_names)):  # type: ignore
            if self.schema_sync:
                note = 'Duplicate labels in header is not supported with "schema_sync"'
                raise FrictionlessException(errors.SchemaError(note=note))
            note = "Schemas with duplicate field names are not supported"
            raise FrictionlessException(errors.SchemaError(note=note))

        return schema

    def detect_lookup(self, resource: Resource):
        """Detect lookup from resource

        Parameters:
            resource (Resource): tabular resource

        Returns:
            dict: lookup
        """
        lookup = {}
        for fk in resource.schema.foreign_keys:

            # Prepare source
            source_name = fk["reference"]["resource"]
            source_key = tuple(fk["reference"]["fields"])
            if source_name != "" and not resource.__package:
                continue
            if source_name:
                if not resource.package.has_resource(source_name):
                    note = f'Failed to handle a foreign key for resource "{resource.name}" as resource "{source_name}" does not exist'
                    raise FrictionlessException(errors.ResourceError(note=note))
                source_res = resource.package.get_resource(source_name)
            else:
                source_res = resource.to_copy()
            source_res.schema.pop("foreignKeys", None)

            # Prepare lookup
            lookup.setdefault(source_name, {})
            if source_key in lookup[source_name]:
                continue
            lookup[source_name][source_key] = set()
            if not source_res:
                continue
            with source_res:
                for row in source_res.row_stream:
                    cells = tuple(row.get(field_name) for field_name in source_key)
                    if set(cells) == {None}:
                        continue
                    lookup[source_name][source_key].add(cells)

        return lookup

    # Metadata

    metadata_Error = errors.DetectorError
    metadata_profile = {
        "properties": {
            "bufferSize": {},
            "samleSize": {},
            "encodingFunction": {},
            "encodingConfidence": {},
            "fieldType": {},
            "fieldNames": {},
            "fieldConfidence": {},
            "fieldFloatNumbers": {},
            "fieldMissingValues": {},
            "fieldTrueValues": {},
            "fieldFalseValues": {},
            "schemaSync": {},
            "schemaPatch": {},
        }
    }
