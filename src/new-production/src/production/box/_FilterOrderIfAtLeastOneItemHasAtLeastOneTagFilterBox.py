from mw_helper import ensure_iterable
from production.box._OrderChangerProductionBox import OrderChangerProductionBox


class FilterOrderIfAtLeastOneItemHasAtLeastOneTagFilterBox(OrderChangerProductionBox):
    def __init__(self, name, sons, allowed_tags, excluded_tags, forbidden_tags, allow_no_tags, filter_type,
                 logger=None):
        super(FilterOrderIfAtLeastOneItemHasAtLeastOneTagFilterBox, self).__init__(name, sons, logger)
        self.allowed_tags = ensure_iterable(allowed_tags)
        self.excluded_tags = ensure_iterable(excluded_tags)
        self.forbidden_tags = ensure_iterable(forbidden_tags)
        self.allow_no_tags = allow_no_tags.lower() == "true"
        self.filter_type = filter_type.lower()

    def change_order(self, order):
        allowed_sale_lines = []
        for item in order.items:
            if self.excluded_item(item):
                continue
            
            if self.allowed_item(item):
                allowed_sale_lines.append(item.line_number)

        if allowed_sale_lines and self.filter_type.lower() == FilterType.by_order.lower():
            return order
        
        order.items = self.filter_allowed_items(allowed_sale_lines, order)
        return order

    def filter_allowed_items(self, allowed_sale_lines, order):
        forbidden_line_numbers = self.forbidden_line_numbers(order)
        allowed_sale_lines = [x for x in allowed_sale_lines if x not in forbidden_line_numbers]
        return [x for x in order.items if x.line_number in allowed_sale_lines]

    def forbidden_line_numbers(self, order):
        return [x.line_number for x in order.items if self.forbidden_item(x)]
    
    def allowed_item(self, item):
        return item.at_least_one_has_at_least_one_tag(self.allowed_tags)
    
    def forbidden_item(self, item):
        if not self.excluded_item(item) and any(x in item.get_tags() for x in self.forbidden_tags):
            return True

        if not self.allow_no_tags and not item.get_tags():
            return True
        
        return False

    def excluded_item(self, item):
        return any(x in item.get_tags() for x in self.excluded_tags)
    

class FilterType(object):
    by_order = "byOrder"
    by_lines = "byLines"
