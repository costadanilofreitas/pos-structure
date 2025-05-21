import json


from report.command import AlignCommand, BoldCommand, FontCommand, RepeatCommand, NewLineCommand

from ._Report import Report
from ._Part import Part
from ._JsonReport import JsonReport


class ReportParser(object):
    def parse(self, report):
        # type: (str) -> Report
        try:
            report_dict = json.loads(report, "utf-8")
        except:
            return None

        if "key" not in report_dict or report_dict["key"] != Report.key:
            return None

        if "parts" not in report_dict or not isinstance(report_dict["parts"], list):
            return None

        parts = []
        for part_dict in report_dict["parts"]:
            text = part_dict["text"]
            commands_json = []
            if "commands" in part_dict:
                commands_json = part_dict["commands"]
                if commands_json is None:
                    commands_json = []

            part_commands = []
            for command in commands_json:
                if command["type"] == "align":
                    part_commands.append(AlignCommand(AlignCommand.Alignment(command["alignment"])))
                elif command["type"] == "bold":
                    part_commands.append(BoldCommand(command["activate"]))
                elif command["type"] == "font":
                    part_commands.append(FontCommand(command["font"]))
                elif command["type"] == "repeat":
                    part_commands.append(RepeatCommand(command["count"], command["text"]))
                elif command["type"] == "newLine":
                    part_commands.append(NewLineCommand())

            parts.append(Part(text, part_commands))

        return JsonReport(parts, report_dict["width"])
