from _Generator import Generator  # noqa
from _Formatter import Formatter  # noqa
from commons.util import Translator


class Report(object):
    def __init__(self, generator, formatter):
        # type:(Generator, Formatter) -> None
        self.generator = generator
        self.formatter = formatter
        self.translator = Translator()

    def generate_and_format_report(self):
        dto = self.generator.generate_data()
        return self.formatter.format_report(dto, self.translator)
