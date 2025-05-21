from mw_helper import ensure_iterable

from ._OrderChangerProductionBox import OrderChangerProductionBox


class ComboTaggedWhenAllHasTagBox(OrderChangerProductionBox):
    def __init__(self, name, sons, tags, tag_to_add, logger=None):
        super(ComboTaggedWhenAllHasTagBox, self).__init__(name, sons, logger)
        self.tags = ensure_iterable(tags)
        self.tag_to_add = tag_to_add

    def change_order(self, order):
        for item in order.items:
            if item.item_type == "COMBO" and self.all_sons_have_tags(item.items):
                item.add_tag(self.tag_to_add)

        return order

    def all_sons_have_tags(self, sons):
        for son in sons:
            if son.item_type != 'OPTION':
                if not son.has_some_tag(self.tags):
                    return False
            else:
                if not self.all_sons_have_tags(son.items):
                    return False
            
        return True

