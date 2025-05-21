from typing import List

from report import Presenter, Part
from report.command import AlignCommand, RepeatCommand
from ..dto import TipReportHeaderDto


class TipReportHeaderPresenter(Presenter):
    def present(self, dto):
        # type: (TipReportHeaderDto) -> List[Part]
        report_header = [
            Part("$TIP_REPORT", [AlignCommand(AlignCommand.Alignment.center)]), a_new_line()
        ]

        report_header.extend([
                Part(
                        "$STORE : {}".format(dto.store_id.zfill(5)),
                        [AlignCommand(AlignCommand.Alignment.left)]), a_new_line()
        ])

        report_header.extend([
            Part("$TIP_REPORT_DATE : #DATE({0}) - #DATE({1})".format(
                dto.start_date.isoformat(),
                dto.end_date.isoformat()),
                [AlignCommand(AlignCommand.Alignment.left)]), a_new_line()])

        report_header.extend([
            Part(
                "$TIP_REPORT_CURRENT_DATE : #DATETIME({})".format(dto.current_date_time.isoformat()),
                [AlignCommand(AlignCommand.Alignment.left)]), a_new_line()
        ])

        report_header.extend([Part(commands=[RepeatCommand(38, "=")]), a_new_line()])
        return report_header


def a_new_line():
    return Part("\n")