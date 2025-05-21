from abc import ABCMeta

from report import Report


class I18nReport(Report):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.i18n = None

    def set_i18n(self, i18n):
        self.i18n = i18n
