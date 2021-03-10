from ..error import Error


class GeneralError(Error):
    code = "general-error"
    name = "General Error"
    template = "General error: {note}"
    description = "There is an error."


class PackageError(GeneralError):
    code = "package-error"
    name = "Package Error"
    template = "The data package has an error: {note}"
    description = "A validation cannot be processed."


class ResourceError(GeneralError):
    code = "resource-error"
    name = "Resource Error"
    template = "The data resource has an error: {note}"
    description = "A validation cannot be processed."


class PipelineError(GeneralError):
    code = "pipeline-error"
    name = "Pipeline Error"
    template = "Pipeline is not valid: {note}"
    description = "Provided pipeline is not valid."


class InquiryError(GeneralError):
    code = "inquiry-error"
    name = "Inquiry Error"
    template = "Inquiry is not valid: {note}"
    description = "Provided inquiry is not valid."


class ControlError(GeneralError):
    code = "control-error"
    name = "Control Error"
    template = "Control is not valid: {note}"
    description = "Provided control is not valid."


class DialectError(GeneralError):
    code = "dialect-error"
    name = "Dialect Error"
    template = "Dialect is not valid: {note}"
    description = "Provided dialect is not valid."


class LayoutError(GeneralError):
    code = "layout-error"
    name = "Layout Error"
    template = "Layout is not valid: {note}"
    description = "Provided layout is not valid."


class SchemaError(GeneralError):
    code = "schema-error"
    name = "Schema Error"
    template = "Schema is not valid: {note}"
    description = "Provided schema is not valid."


class FieldError(GeneralError):
    code = "field-error"
    name = "Field Error"
    template = "Field is not valid: {note}"
    description = "Provided field is not valid."


class ReportError(GeneralError):
    code = "report-error"
    name = "Report Error"
    template = "Report is not valid: {note}"
    description = "Provided report is not valid."


class StatusError(GeneralError):
    code = "status-error"
    name = "Status Error"
    template = "Status is not valid: {note}"
    description = "Provided status is not valid."


class CheckError(GeneralError):
    code = "check-error"
    name = "Check Error"
    template = "Check is not valid: {note}"
    description = "Provided check is not valid"


class StepError(GeneralError):
    code = "step-error"
    name = "Step Error"
    template = "Step is not valid: {note}"
    description = "Provided step is not valid"


class SourceError(GeneralError):
    code = "source-error"
    name = "Source Error"
    template = "The data source has not supported or has inconsistent contents: {note}"
    description = "Data reading error because of not supported or inconsistent contents."


class SchemeError(GeneralError):
    code = "scheme-error"
    name = "Scheme Error"
    template = "The data source could not be successfully loaded: {note}"
    description = "Data reading error because of incorrect scheme."


class FormatError(GeneralError):
    code = "format-error"
    name = "Format Error"
    template = "The data source could not be successfully parsed: {note}"
    description = "Data reading error because of incorrect format."


class EncodingError(GeneralError):
    code = "encoding-error"
    name = "Encoding Error"
    template = "The data source could not be successfully decoded: {note}"
    description = "Data reading error because of an encoding problem."


class HashingError(GeneralError):
    code = "hashing-error"
    name = "Hashing Error"
    template = "The data source could not be successfully hashed: {note}"
    description = "Data reading error because of a hashing problem."


class CompressionError(GeneralError):
    code = "compression-error"
    name = "Compression Error"
    template = "The data source could not be successfully decompressed: {note}"
    description = "Data reading error because of a decompression problem."


class StorageError(GeneralError):
    code = "storage-error"
    name = "Storage Error"
    template = "The storage has an error: {note}"
    description = "A storage's operation cannot be performed"


class TaskError(GeneralError):
    code = "task-error"
    name = "Task Error"
    template = "The task has an error: {note}"
    description = "General task-level error."
