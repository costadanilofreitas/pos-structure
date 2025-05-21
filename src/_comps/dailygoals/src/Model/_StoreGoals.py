class StoreGoals(object):
    def __init__(self, amount_goal, average_sale_goal, operator_sale_goal, item_goals):
        self.amount_goal = amount_goal
        self.average_sale_goal = average_sale_goal
        self.operator_sale_goal = operator_sale_goal
        self.sold_quantity = 0
        self.item_goals = item_goals
