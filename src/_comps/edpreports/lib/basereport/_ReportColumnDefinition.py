from basereport._AlignTypes import AlignTypes


class ReportColumnDefinition(object):
    def __init__(
            self,
            text='',
            width=38,
            fill_with_char=' ',
            before_text='',
            after_text='',
            align=AlignTypes.LEFT,
            after_fill_text='',
            before_fill_text=''):
        # type: (str, int, unicode, str, str, AlignTypes, str, str) -> None
        self.text = text
        self.width = width
        self.fill_with_char = fill_with_char
        self.before_text = before_text
        self.after_text = after_text
        self.align = align
        self.after_fill_text = after_fill_text
        self.before_fill_text = before_fill_text
