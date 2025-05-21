from escposformatter import DefaultEscPosFormatter
from htmlformatter import HtmlFormatter
from report import ReportParser
from sysactions import generate_report, print_text, show_print_preview, show_messagebox

from enum import Enum


class PrinterType(Enum):
    esc_pos = "ESC_POS"
    apos = "APOS"


def print_report(pos_id, report_name, preview, *args):
    report_data = generate_report(report_name, pos_id, *args)

    report = ReportParser().parse(report_data)
    if report is not None:
        if preview:
            print_preview_report = HtmlFormatter().format(report)
            if show_print_preview(pos_id, print_preview_report.encode("utf-8")) in (1, None):
                return False

        text = DefaultEscPosFormatter().format(report)
        print_text(pos_id, None, text)
    elif report is None:
        show_messagebox(pos_id, "$NO_REPORT_DATA", "$ERROR")
    else:
        return print_text(pos_id, None, report_data, preview)
