from __future__ import annotations

import codecs
import os
from copy import copy, deepcopy
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import attrs

from .. import helpers, settings
from ..dialect import Dialect
from ..exception import FrictionlessException
from ..fields import AnyField
from ..metadata import Metadata
from ..platform import platform
from ..schema import Field, Schema

if TYPE_CHECKING:
    from .. import types
    from ..resource import Resource


@attrs.define(kw_only=True, repr=False)
class Detector:
    """Detector representation.

    This main purpose of this class is to set the parameters to define
    how different aspects of metadata are detected.

    """

    buffer_size: int = settings.DEFAULT_BUFFER_SIZE
    """
    The amount of bytes to be extracted as a buffer. It defaults to 10000.
    The buffer_size can be increased to improve the inference accuracy to
    detect file encoding.
    """

    sample_size: int = settings.DEFAULT_SAMPLE_SIZE
    """
    The amount of rows to be extracted as a sample for dialect/schema inferring.
    It defaults to 100. The sample_size can be increased to improve the inference
    accuracy.
    """

    encoding_function: Optional[types.IEncodingFunction] = None
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

    field_missing_values: List[str] = attrs.field(
        factory=settings.DEFAULT_MISSING_VALUES.copy,
    )
    """
    String to be considered as missing values.
    For more information, please check "Describing  Data" guide.
    It defaults to `['']`
    """

    field_true_values: List[str] = attrs.field(
        factory=settings.DEFAULT_TRUE_VALUES.copy,
    )
    """
    String to be considered as true values.
    For more information, please check "Describing  Data" guide.
    It defaults to `["true", "True", "TRUE", "1"]`
    """

    field_false_values: List[str] = attrs.field(
        factory=settings.DEFAULT_FALSE_VALUES.copy,
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
    provide a subset of fields to be applied on top of the inferred
    fields or the provided schema can have different order of fields.
    """

    schema_patch: Optional[Dict[str, Any]] = None
    """
    A dictionary to be used as an inferred schema patch.
    The form of this dictionary should follow the Schema descriptor form
    except for the `fields` property which should be a mapping with the
    key named after a field name and the values being a field patch.
    For more information, please check "Extracting Data" guide.
    """

    # Metadta

    # TODO: remove static method?
    @staticmethod
    def detect_metadata_type(
        source: Any, *, format: Optional[str] = None
    ) -> Optional[str]:
        """Return an descriptor type as 'resource' or 'package'"""
        source = helpers.normalize_source(source)

        # String
        if isinstance(source, str):
            for type, item in settings.METADATA_TRAITS.items():
                if source.endswith(tuple(item["names"])):
                    return type
            format = format or helpers.parse_scheme_and_format(source)[1]
            if format in ["json", "yaml"]:
                try:
                    size = settings.DEFAULT_BUFFER_SIZE * 10
                    source = Metadata.metadata_retrieve(source, size=size)
                except Exception:
                    pass

        # Mapping
        if isinstance(source, dict):
            for type, item in settings.METADATA_TRAITS.items():
                if set(item["props"]).intersection(source.keys()):  # type: ignore
                    return type

    # Resource

    def detect_resource(self, resource: Resource) -> None:
        """Detects path details"""
        name = "memory"
        scheme = None
        format = None
        compression = None

        # Detect details
        if resource.path:
            names: List[str] = []
            for part in [resource.path] + (resource.extrapaths or []):
                name = os.path.splitext(os.path.basename(part))[0]
                names.append(name)
            name = os.path.commonprefix(names)
            name = helpers.slugify(name, regex_pattern=r"[^-a-z0-9._/]")
            name = name or "name"
            scheme, format = helpers.parse_scheme_and_format(resource.path)
            if format in settings.COMPRESSION_FORMATS:
                compression = format
                path = resource.path[: -len(format) - 1]
                if resource.innerpath:
                    path = os.path.join(path, resource.innerpath)
                scheme, format = helpers.parse_scheme_and_format(path)
                if format:
                    name = os.path.splitext(name)[0]

        # Save details
        resource.name = resource.name or name
        resource.scheme = resource.scheme or scheme
        resource.format = resource.format or format
        resource.compression = resource.compression or compression

    # Encoding

    def detect_encoding(
        self, buffer: types.IBuffer, *, encoding: Optional[str] = None
    ) -> str:
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
            detector = platform.chardet.UniversalDetector()
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

    # Dialect

    def detect_dialect(
        self,
        sample: types.ISample,
        *,
        dialect: Optional[Dialect] = None,
    ) -> Dialect:
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
            # We use it to eliminate initial rows that are comments/etc

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

    # Schema

    # TODO: detect fields without type
    def detect_schema(
        self,
        fragment: types.IFragment,
        *,
        labels: Optional[List[str]] = None,
        schema: Optional[Schema] = None,
        field_candidates: List[Dict[str, Any]] = settings.DEFAULT_FIELD_CANDIDATES,
        **options: Any,
    ) -> Schema:
        """Detect schema from fragment

        Parameters:
            fragment (any[][]): data fragment
            labels? (str[]): data labels
            schema? (Schema): data schema

        Returns:
            Schema: schema
        """

        # Create schema
        if not schema:
            schema = Schema(fields=[])

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
                names[index] = name or f"field{index + 1}"

            # Deduplicate names
            if len(names) != len(set(names)):
                seen_names: List[str] = []
                names = names.copy()
                for index, name in enumerate(names):
                    count = seen_names.count(name) + 1
                    names[index] = "%s%s" % (name, count) if count > 1 else name
                    seen_names.append(name)

            # Handle type/empty
            if self.field_type or not fragment:
                type = self.field_type or settings.DEFAULT_FIELD_TYPE
                schema.fields = []
                for name in names:
                    field = Field.from_descriptor({"name": name, "type": type})
                    schema.add_field(field)
                return schema

            # Prepare runners
            runners: List[List[Any]] = []
            runner_fields: List[Field] = []  # we use shared fields
            for candidate in field_candidates:
                descriptor = candidate.copy()
                descriptor["name"] = "shared"
                field = Field.from_descriptor(descriptor)
                if field.type == "number" and self.field_float_numbers:
                    field.float_number = True  # type: ignore
                elif field.type == "boolean":
                    if self.field_true_values != settings.DEFAULT_TRUE_VALUES:
                        field._descriptor.true_values = self.field_true_values  # type: ignore
                    if self.field_false_values != settings.DEFAULT_FALSE_VALUES:
                        field._descriptor.false_values = self.field_false_values  # type: ignore
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
                    fields[index] = AnyField(name=name, schema=schema)  # type: ignore
            schema.fields = fields  # type: ignore

        # Sync schema
        if self.schema_sync:
            if labels:
                case_sensitive = options["header_case"]

                if not case_sensitive:
                    labels = [label.lower() for label in labels]

                if len(labels) != len(set(labels)):
                    note = '"schema_sync" requires unique labels in the header'
                    raise FrictionlessException(note)

                mapped_fields = self.mapped_schema_fields_names(
                    schema.fields,  # type: ignore
                    case_sensitive,
                )

                self.rearrange_schema_fields_given_labels(
                    mapped_fields,
                    schema,
                    labels,
                )

                self.add_missing_required_labels_to_schema_fields(
                    mapped_fields, schema, labels, case_sensitive
                )

        # Patch schema
        if self.schema_patch:
            patch = deepcopy(self.schema_patch)
            patch_fields = patch.pop("fields", {})
            descriptor = schema.to_descriptor()
            descriptor.update(patch)
            for field_descriptor in descriptor.get("fields", []):
                field_name = field_descriptor.get("name")
                field_patch = patch_fields.get(field_name, {})  # type: ignore
                field_descriptor.update(field_patch)
            schema = Schema.from_descriptor(descriptor)

        return schema

    @staticmethod
    def mapped_schema_fields_names(
        fields: List[Field], case_sensitive: bool
    ) -> Dict[str, Field]:
        """Create a dictionnary to map field names with schema fields"""
        if case_sensitive:
            return {field.name: field for field in fields}
        else:
            return {field.name.lower(): field for field in fields}

    @staticmethod
    def rearrange_schema_fields_given_labels(
        fields_mapping: Dict[str, Field],
        schema: Schema,
        labels: List[str],
    ):
        """Rearrange fields according to the order of labels. All fields
        missing from labels are dropped"""
        schema.clear_fields()

        for name in labels:
            default_field = Field.from_descriptor({"name": name, "type": "any"})
            field = fields_mapping.get(name, default_field)
            schema.add_field(field)

    def add_missing_required_labels_to_schema_fields(
        self,
        fields_mapping: Dict[str, Field],
        schema: Schema,
        labels: List[str],
        case_sensitive: bool,
    ):
        """This method aims to add missing required labels and
        primary key field not in labels to schema fields.
        """
        for name, field in fields_mapping.items():
            if (
                self.field_is_required(field, schema, case_sensitive)
                and name not in labels
            ):
                schema.add_field(field)

    @staticmethod
    def field_is_required(
        field: Field,
        schema: Schema,
        case_sensitive: bool,
    ) -> bool:
        if case_sensitive:
            return field.required or field.name in schema.primary_key
        else:
            lower_primary_key = [pk.lower() for pk in schema.primary_key]
            return field.required or field.name.lower() in lower_primary_key
