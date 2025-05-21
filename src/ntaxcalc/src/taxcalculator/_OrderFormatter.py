from pos_model import Order

from _TaxItemFormatter import TaxItemFormatter


class OrderFormatter(object):
    pattern = '<?xml version="1.0" encoding="UTF-8"?>\n'
    pattern += '<Order posId=\"{pos_id}\" orderId=\"{order_id}\">{tax_items}</Order>'

    def __init__(self, tax_item_formatter):
        # type: (TaxItemFormatter) -> None
        self.tax_item_formatter = tax_item_formatter

    def format_order(self, order):
        # type: (Order) -> str
        tax_items_str = ''
        for sale_item in order.sale_items:
            for tax_item in sale_item.taxes:
                tax_items_str += self.tax_item_formatter.format_tax_item(tax_item, sale_item)

        formatted_order = self.pattern.format(
            pos_id=order.pos_id,
            order_id=order.order_id,
            tax_items=tax_items_str)

        return formatted_order
