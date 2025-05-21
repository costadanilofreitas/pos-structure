from ._Command import Command


class BoldCommand(Command):
    def __init__(self, activate):
        self.activate = activate
