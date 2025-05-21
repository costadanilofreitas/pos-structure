from typing import Dict


class ViewConfiguration(object):
    def __init__(self, name, view_type, log_level, extra_config):
        # type: (str, str, str, Dict[str, str]) -> None
        self.name = name
        self.type = view_type
        self.log_level = log_level
        self.extra_config = extra_config
