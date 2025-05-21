import json


from ._Report import Report
from ._Part import Part


class ReportParser(object):
    def parse(self, report):
        try:
            report_dict = json.loads(report, "utf-8")
        except:
            return None

        if "key" not in report_dict or report_dict["key"] != Report.key:
            return None

        if "parts" not in report_dict or not isinstance(report_dict["parts"], list):
            return None

        parts = []
        for part_dict in report_dict["parts"]:
            parts.append(Part(part_dict["text"]))

        return parts
