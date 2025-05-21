from basereport import I18n
from report import Reporter, Presenter, Generator

from ._I18nReport import I18nReport


class I18nReporter(Reporter):
    def __init__(self, generator, presenter, i18n):
        # type: (Generator, Presenter, I18n) -> None
        self.i18n = i18n
        super(I18nReporter, self).__init__(generator, I18nPresenter(presenter, self.i18n))


class I18nPresenter(Presenter):
    def __init__(self, base_presenter, i18n):
        # type: (Presenter, I18n) -> None
        self.base_presenter = base_presenter
        self.i18n = i18n

    def present(self, dto):
        report = self.base_presenter.present(dto)
        if isinstance(report, I18nReport):
            report.set_i18n(self.i18n)

        return report
