class NotValidSolution(Exception):
    def __init__(self, option_part_code, part_code):
        self.option_part_code = option_part_code
        self.part_code = part_code
