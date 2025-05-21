from typing import List


class DefaultOption(object):
    def __init__(self, option_code, part_codes):
        # type: (int, List[int]) -> None
        self.option_code = option_code
        self.part_codes = part_codes
