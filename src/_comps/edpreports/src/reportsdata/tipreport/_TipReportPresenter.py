from basereport import SimpleReport
from report import Presenter
from typing import List

from .dto import TipReportDto
from .presenter import TipReportHeaderPresenter, TipReportBodyPresenter


class TipReportPresenter(Presenter):
    def present(self, dto):
        # type: (TipReportDto) -> SimpleReport
        presenters = [
            (TipReportHeaderPresenter(), dto.header),
            (TipReportBodyPresenter(), dto.body)
        ]  # type: List[Presenter]

        report = []
        for presenter, dto in presenters:
            report.extend(presenter.present(dto))

        return SimpleReport(report)

