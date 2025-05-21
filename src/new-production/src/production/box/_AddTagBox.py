from mw_helper import ensure_list, convert_to_dict

from ._OrderChangerProductionBox import OrderChangerProductionBox


class AddTagBox(OrderChangerProductionBox):

    def __init__(self, name, sons, tag, items, logger=None):
        super(AddTagBox, self).__init__(name, sons, logger)
        self.items = convert_to_dict(ensure_list(items))
        self.tag = tag

    def change_order(self, order):
        for item in order.items:
            self.add_tag_on_item(item)

        return order

    def add_tag_on_item(self, item):
        if item.part_code in self.items and item.does_not_have_tag(self.tag):
            item.add_tag(self.tag)
            
        for son in item.items:
            self.add_tag_on_item(son)
