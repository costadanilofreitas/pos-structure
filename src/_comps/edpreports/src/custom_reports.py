import os
import sys

import helper

from mwposreport import ReporterFactory
from old_helper import get_class_by_name
import reports


def main():
    helper.import_pydevd(os.environ["LOADERCFG"], 9124)
    current_module = sys.modules[__name__]

    available_reports = []
    for _, dir_names, _ in os.walk(os.path.join(os.path.dirname(__file__), "reportsentry")):
        available_reports = dir_names
        break

    for report in available_reports:
        setattr(current_module, report, create_wrapper(report, _custom_report_impl))


def _custom_report_impl(report_name, pos_id, *args, **kwargs):
    complete_class_name = "reportsentry." + report_name + ".ReportGenerator"

    report_class = get_class_by_name(unicode(complete_class_name))

    report = getattr(report_class, "generate")(reports.mbcontext, pos_id, *args, **kwargs)
    if isinstance(report, tuple):
        generator = report[0]
        presenter = report[1]
        report_data = ReporterFactory.build_reporter(pos_id, generator, presenter).create_report()
        return report_data
    else:
        return report


def create_wrapper(name, func):
    def wrapper(*args, **kwargs):
        return func(name, args[0], *args[1:], **kwargs)

    return wrapper


main()
