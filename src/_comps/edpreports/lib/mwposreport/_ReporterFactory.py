from basereport import I18n, I18nReporter

from ._MwI18nRepository import MwI18nRepository


class ReporterFactory(object):
    @staticmethod
    def build_reporter(pos_id, generator, presenter):
        i18n_repository = MwI18nRepository(pos_id)
        i18n = I18n(i18n_repository)
        return I18nReporter(generator, presenter, i18n)
