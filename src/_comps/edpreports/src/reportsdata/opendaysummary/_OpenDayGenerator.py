from commons.report import Generator
from reports_app.opendaysummary.dto import OpenDaySummaryInfo  # noqa
from reports_app.opendaysummary.dto import OpenDaySummaryDto  # noqa
from reports_app.opendaysummary.dto import OpenDaySummaryHeaderDto
from reports_app.opendaysummary.dto import OpenDaySummaryBodyDto


class OpenDayGenerator(Generator):
    def __init__(self, open_day_summary_info):
        # type: (OpenDaySummaryInfo) -> ()
        self.open_day_summary_info = open_day_summary_info

    def generate_data(self):
        # type: (OpenDaySummaryInfo) -> OpenDaySummaryDto
        open_day_summary_header_dto = OpenDaySummaryHeaderDto(
            self.open_day_summary_info.pos_id,
            self.open_day_summary_info.store_id,
            self.open_day_summary_info.operator_id,
            self.open_day_summary_info.business_date
        )
        open_day_summary_body_dto = OpenDaySummaryBodyDto(
            self.open_day_summary_info.authorizer
        )

        return OpenDaySummaryDto(open_day_summary_header_dto, open_day_summary_body_dto)
