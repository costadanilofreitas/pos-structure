from typing import Dict, List, Union


class BoxConfiguration(object):
    def __init__(self, name, box_type, sons, log_level, extra_config):
        # type: (str, str, Union[str, List[str]], str, Dict[str, str]) -> None
        self.name = name
        self.type = box_type
        self.sons = sons
        self.log_level = log_level
        self.extra_config = extra_config
