from basereport import SimpleReport
from report import Presenter, Part
from report.command import BoldCommand, NewLineCommand, AlignCommand


class SampleReportPresenter(Presenter):

    def present(self, dto):
        parts = [
            Part("$OPERATOR"),
            Part(None, [NewLineCommand()]),
            Part("$OPERATOR"),
            Part(None, [BoldCommand(True)]),
            Part("$TABLE $SIGN_IN"),
            Part(None, [BoldCommand(False)]),
            Part("$OPERATOR"),
            Part(None, [NewLineCommand()]),

            Part("$OPERATOR"),
            Part(None, [BoldCommand(True)]),
            Part("$TABLE $SIGN_IN"),
            Part(None, [NewLineCommand()]),
            Part("$TABLE $SIGN_IN "), Part("$TABLE $SIGN_IN"),
            Part(None, [NewLineCommand()]),
            Part("$OPERATOR"),
            Part(None, [BoldCommand(False)]),
            Part(" $OPERATOR"),
            Part(None, [NewLineCommand()]),


            Part(None, [AlignCommand(AlignCommand.Alignment.left)]),
            Part("$TABLE $SIGN_IN"), Part("$ORDER $OPERATOR"),
            Part(None, [NewLineCommand()]),
            Part(None, [AlignCommand(AlignCommand.Alignment.center)]),
            Part("$TABLE $SIGN_IN"), Part("$ORDER $OPERATOR"),
            Part(None, [NewLineCommand()]),
            Part(None, [AlignCommand(AlignCommand.Alignment.right)]),
            Part("$TABLE $SIGN_IN"), Part("$ORDER $OPERATOR"),
            Part(None, [NewLineCommand()])
        ]
        return SimpleReport(parts, 38)
