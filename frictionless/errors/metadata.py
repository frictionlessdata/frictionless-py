from __future__ import annotations
from ..error import Error


class MetadataError(Error):
    type = "metadata-error"
    title = "Metadata Error"
    description = "There is a metadata error."
    template = "Metadata error: {note}"


class CatalogError(MetadataError):
    type = "catalog-error"
    title = "Catalog Error"
    description = "A validation cannot be processed."
    template = "The data catalog has an error: {note}"


class ChecklistError(MetadataError):
    type = "checklist-error"
    title = "Checklist Error"
    description = "Provided checklist is not valid."
    template = "Checklist is not valid: {note}"


class CheckError(ChecklistError):
    type = "check-error"
    title = "Check Error"
    description = "Provided check is not valid"
    template = "Check is not valid: {note}"


class DetectorError(MetadataError):
    type = "detector-error"
    title = "Detector Error"
    description = "Provided detector is not valid."
    template = "Detector is not valid: {note}"


class DialectError(MetadataError):
    type = "dialect-error"
    title = "Dialect Error"
    description = "Provided dialect is not valid."
    template = "Dialect is not valid: {note}"


class ControlError(DialectError):
    type = "control-error"
    title = "Control Error"
    description = "Provided control is not valid."
    template = "Control is not valid: {note}"


class InquiryError(MetadataError):
    type = "inquiry-error"
    title = "Inquiry Error"
    description = "Provided inquiry is not valid."
    template = "Inquiry is not valid: {note}"


class InquiryTaskError(MetadataError):
    type = "inquiry-task-error"
    title = "Inquiry Task Error"
    description = "Provided inquiry task is not valid."
    template = "Inquiry task is not valid: {note}"


class PackageError(MetadataError):
    type = "package-error"
    title = "Package Error"
    description = "A validation cannot be processed."
    template = "The data package has an error: {note}"


class PipelineError(MetadataError):
    type = "pipeline-error"
    title = "Pipeline Error"
    description = "Provided pipeline is not valid."
    template = "Pipeline is not valid: {note}"


class StepError(PipelineError):
    type = "step-error"
    title = "Step Error"
    description = "Provided step is not valid"
    template = "Step is not valid: {note}"


class ReportError(MetadataError):
    type = "report-error"
    title = "Report Error"
    description = "Provided report is not valid."
    template = "Report is not valid: {note}"


class ReportTaskError(ReportError):
    type = "report-task-error"
    title = "Report Task Error"
    description = "Provided report task is not valid."
    template = "Report task is not valid: {note}"


class SchemaError(MetadataError):
    type = "schema-error"
    title = "Schema Error"
    description = "Provided schema is not valid."
    template = "Schema is not valid: {note}"


class FieldError(SchemaError):
    type = "field-error"
    title = "Field Error"
    description = "Provided field is not valid."
    template = "Field is not valid: {note}"


class StatsError(MetadataError):
    type = "stats-error"
    title = "Stats Error"
    description = "Stats object has an error."
    template = "Stats object has an error: {note}"
