from .config import REPORT_PROFILE


class Report(dict):
    def __init__(self, report):
        super().__init__(report)

    def validate(self):
        print(REPORT_PROFILE)


class ReportTable:
    pass
