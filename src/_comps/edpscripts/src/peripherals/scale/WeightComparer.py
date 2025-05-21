class WeightComparer(object):
    def __init__(self):
        self.previous_weight = None

    def is_weight_equal_to_previous(self, weight):
        if self.previous_weight == weight:
            return True
        else:
            self.previous_weight = weight
            return False
