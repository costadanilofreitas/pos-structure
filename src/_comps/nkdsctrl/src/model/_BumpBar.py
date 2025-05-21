import cfgtools

from util import find_key_value, find_key_values

from ._BumpBarCommand import BumpBarCommand


class BumpBar(object):
    def __init__(self, group):
        # type: (cfgtools.Group) -> BumpBar
        self.name = ''
        self.simulate_bump_bar = True
        self.commands = []

        self.parse_bump_bar(group)

    def parse_bump_bar(self, bump_bar_group):
        # type: (cfgtools.Group) -> ()
        self.name = bump_bar_group.name
        self.simulate_bump_bar = find_key_value(bump_bar_group, "SimulateBumpBar").lower() == 'true'
        command_group = next((x for x in bump_bar_group.groups if x.name == "Commands"), [])

        for command in command_group.keys:
            self.commands.append(BumpBarCommand(command.name, command.values[0].split("|")))

