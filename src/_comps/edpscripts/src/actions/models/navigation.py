class Navigation(object):
    def __init__(self, nav_id, name, parent_nav_id, sort_order, button_text, background_color):
        self.nav_id = nav_id
        self.name = name
        self.parent_nav_id = parent_nav_id
        self.sort_order = sort_order
        self.button_text = button_text
        self.background_color = background_color
        self.groups = []
        self.items = []
