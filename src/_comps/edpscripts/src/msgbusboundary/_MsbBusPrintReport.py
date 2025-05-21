from application.domain import PrintReport
from sysactions import get_model, print_report


class MsbBusPrintReport(PrintReport):
    def send_print(self, pos_id, preview, report_name, *report_params):
        model = get_model(pos_id)
        return print_report(pos_id, model, preview, report_name, *report_params)
