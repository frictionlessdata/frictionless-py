from ..error import Error


class InquiryError(Error):
    code = "inquiry-error"
    name = "Inquiry Error"
    template = "Inquiry is not valid: {note}"
    description = "Provided inquiry is not valid."
