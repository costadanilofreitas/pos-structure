from typing import List, Union  # noqa

from ._I18nReport import I18nReport
from report import Part  # noqa
from report import Report


class SimpleReport(I18nReport):
    def __init__(self, parts, width=40):
        # type: (List[Union[Part, Report]]) -> None
        self.parts = parts
        self.width = width
        self.i18n = None

    def get_parts(self):
        parts = []
        only_parts = self.filter_parts()
        i18n_parts = self.internationalize(only_parts)
        count = 0
        for i in range(0, len(self.parts)):
            if isinstance(self.parts[i], Report):
                parts.extend(self.parts[i].get_parts())
            else:
                parts.append(i18n_parts[count])
                count += 1

        return parts

    def get_width(self):
        return self.width

    def set_i18n(self, i18n):
        super(SimpleReport, self).set_i18n(i18n)
        for part in self.parts:
            if isinstance(part, I18nReport):
                part.set_i18n(i18n)

    def filter_parts(self):
        return filter(lambda x: isinstance(x, Part), self.parts)

    def internationalize(self, parts):
        ret_parts = []
        for part in parts:
            if part.text is not None:
                ret_parts.append(Part(self.i18n.internationalize_text(part.text), commands=part.commands))
            else:
                ret_parts.append(part)

        return ret_parts
