import json

from ._Generator import Generator  # noqa
from ._Presenter import Presenter  # noqa
from ._ReportJSONEncoder import ReportJSONEncoder


class Reporter(object):
    def __init__(self, generator, presenter):
        # type: (Generator, Presenter) -> None
        self.generator = generator
        self.presenter = presenter

    def create_report(self):
        dto = self.generator.generate_data()
        report = self.presenter.present(dto)
        return json.dumps(report.get_parts(), cls=ReportJSONEncoder, encoding="utf-8")
