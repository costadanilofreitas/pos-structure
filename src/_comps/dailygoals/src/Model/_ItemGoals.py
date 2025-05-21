class ItemGoals(object):
    def __init__(self, name, part_codes, quantity_goal, quantity_operator_goal, quantity_sold):
        self.name = name
        self.part_codes = part_codes
        self.quantity_goal = quantity_goal
        self.quantity_operator_goal = quantity_operator_goal
        self.quantity_sold = quantity_sold
