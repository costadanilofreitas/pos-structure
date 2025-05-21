class ParentIsNotAnOption(Exception):
    def __init__(self, part_code):
        self.part_code = part_code
