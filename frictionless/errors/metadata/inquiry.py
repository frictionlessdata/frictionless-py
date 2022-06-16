from .metadata import MetadataError


class InquiryError(MetadataError):
    code = "inquiry-error"
    name = "Inquiry Error"
    template = "Inquiry is not valid: {note}"
    description = "Provided inquiry is not valid."
