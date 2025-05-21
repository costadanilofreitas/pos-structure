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
        report = self.create_base_report()
        return json.dumps(report, cls=ReportJSONEncoder, encoding="utf-8")

    def create_base_report(self):
        dto = self.generator.generate_data()
        return self.presenter.present(dto)
