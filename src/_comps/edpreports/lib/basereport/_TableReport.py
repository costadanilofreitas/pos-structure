from report import Part
from typing import List, Union, Optional  # noqa


from ._AlignTypes import AlignTypes
from ._ReportColumnDefinition import ReportColumnDefinition
from ._I18nReport import I18nReport


class TableReport(I18nReport):
    def __init__(self, lines=None, column_definitions=None):
        # type: (List[List[Union[str, ReportColumnDefinition]]], Optional[List[ReportColumnDefinition]]) -> None
        self.lines = lines
        self.column_definitions = column_definitions

    def get_parts(self):
        translated_lines = TableTranslator(self.i18n).translate(self.lines)

        report = []
        for line in translated_lines:
            report.extend(self._format_line(line))
        return report

    def _format_line(self, line):
        report_line = []
        current_column = 0
        for cell in line:
            if not cell:
                continue
            
            line_text = self._format_cell(cell, current_column)
            report_line.append(Part(text=line_text))
            current_column += 1
        report_line.append(Part(text="\n"))
        return report_line

    def _format_cell(self, cell, current_column):
        cell_format = self._get_cell_format(cell, current_column)
        cell_text = self._get_cell_text(cell)
        return self._get_formatted_text(cell_format, cell_text)

    def _get_cell_format(self, cell, current_column):
        if isinstance(cell, ReportColumnDefinition):
            return cell
        else:
            return self.column_definitions[current_column]

    @staticmethod
    def _get_cell_text(cell):
        if isinstance(cell, ReportColumnDefinition):
            return cell.text
        else:
            return cell

    def _get_formatted_text(self, cell_format, cell_text):
        text = self._truncate_text(cell_format, cell_text)
        text = cell_format.before_text + text + cell_format.after_text
        text = self._fill_with_character(cell_format, text)

        return text

    def _truncate_text(self, cell_format, cell_text):
        reduced_cell_text = cell_text
        size_to_reduce = self.calculate_size_to_reduce(cell_format, cell_text)
        if size_to_reduce > 0:
            reduced_cell_text = cell_text[0:len(cell_text) - size_to_reduce]
        return reduced_cell_text

    @staticmethod
    def calculate_size_to_reduce(cell_format, cell_text):
        total_size = len(cell_text)
        total_size += len(cell_format.before_text) + len(cell_format.after_text)
        total_size += len(cell_format.before_fill_text) + len(cell_format.after_fill_text)
        size_to_reduce = total_size - cell_format.width
        return size_to_reduce

    def _fill_with_character(self, cell_format, text):
        fill_char = cell_format.fill_with_char
        if fill_char == "":
            fill_char = " "

        quantity = cell_format.width - len(text) - len(cell_format.after_fill_text) - len(cell_format.before_fill_text)

        if cell_format.align == AlignTypes.LEFT:
            text = self._add_fill_char_after(fill_char, quantity, text)
        elif cell_format.align == AlignTypes.RIGHT:
            text = self._add_fill_char_before(fill_char, quantity, text)
        else:
            text = self._add_fill_char_aroud(fill_char, quantity, text)

        return cell_format.before_fill_text + text + cell_format.after_fill_text

    @staticmethod
    def _add_fill_char_after(fill_char, fill_with_char_quantity, text):
        return text + (fill_char * fill_with_char_quantity)

    @staticmethod
    def _add_fill_char_before(fill_char, fill_with_char_quantity, text):
        return (fill_char * fill_with_char_quantity) + text

    @staticmethod
    def _add_fill_char_aroud(fill_char, fill_with_char_quantity, text):
        text = "{}{}{}".format(fill_char * (fill_with_char_quantity / 2),
                               text,
                               fill_char * (fill_with_char_quantity / 2))
        if fill_with_char_quantity % 2 == 1:
            text += fill_char
        return text


class TableTranslator(object):
    def __init__(self, i18n):
        self.i18n = i18n

    def translate(self, lines):
        translated_lines = []
        for line in lines:
            translated_line = []
            for cell in line:
                text = self.get_cell_text(cell)
                try:
                    translated_text = self.i18n.internationalize_text(text)
                    text = self.create_translated_cell(cell, translated_text)
                except Exception as _:
                    pass
                
                translated_line.append(self.create_translated_cell(cell, text))
                    
            translated_lines.append(translated_line)

        return translated_lines

    @staticmethod
    def get_cell_text(cell):
        if isinstance(cell, ReportColumnDefinition):
            text = cell.text
        else:
            text = cell
        return text

    @staticmethod
    def create_translated_cell(cell, translated_text):
        if isinstance(cell, ReportColumnDefinition):
            return ReportColumnDefinition(text=translated_text,
                                          width=cell.width,
                                          fill_with_char=cell.fill_with_char,
                                          before_text=cell.before_text,
                                          after_text=cell.after_text,
                                          align=cell.align,
                                          after_fill_text=cell.after_fill_text,
                                          before_fill_text=cell.before_fill_text)
        else:
            return translated_text
