from ..check import Check


class BaselineCheck(Check):
    def validate_headers(self, headers):
        return headers.errors

    def validate_row(self, row):
        return row.errors
