class ToggleTagLineRequest(object):
    def __init__(self, order_id, view, lines, tag_name):
        self.order_id = order_id
        self.view = view
        self.lines = lines
        self.tag_name = tag_name
