from _Command import Command


class RepeatCommand(Command):
    def __init__(self, count, text):
        self.count = count
        self.text = text
