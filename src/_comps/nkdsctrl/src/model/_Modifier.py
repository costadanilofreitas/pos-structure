import cfgtools


class Modifier(object):
    def __init__(self, key):
        # type: (cfgtools.Key) -> Modifier
        self.name = ''
        self.description = 0

        self.parse_modifier(key)

    def parse_modifier(self, modifier_key):
        # type: (cfgtools.Key) -> ()
        self.name = modifier_key.name
        self.description = modifier_key.values[0]
