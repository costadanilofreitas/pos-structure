from json import JSONEncoder

from report.command import NewLineCommand

from ._Report import Report
from ._Part import Part
from .command import AlignCommand, BoldCommand, FontCommand, RepeatCommand


class ReportJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Report):
            return {
                "key": Report.key,
                "width": o.get_width(),
                "parts": o.get_parts()
            }

        if isinstance(o, Part):
            return {
                "text": o.text,
                "commands": o.commands
            }

        if isinstance(o, AlignCommand):
            return {
                "type": "align",
                "alignment": o.alignment.value
            }

        if isinstance(o, BoldCommand):
            return {
                "type": "bold",
                "activate": o.activate
            }

        if isinstance(o, FontCommand):
            return {
                "type": "font",
                "font": o.font.value
            }

        if isinstance(o, RepeatCommand):
            return {
                "type": "repeat",
                "text": o.text,
                "count": o.count
            }

        if isinstance(o, NewLineCommand):
            return {
                "type": "newLine"
            }

        return JSONEncoder.default(self, o)
