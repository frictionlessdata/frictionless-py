from ..check import Check


class BaselineCheck(Check):
    def validate_table_headers(self, headers):
        return headers.errors

    def validate_table_row(self, row):
        return row.errors
