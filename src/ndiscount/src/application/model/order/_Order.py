from json import dumps, loads
from xml.etree import cElementTree as eTree

from application.model.benefit import AppliedBenefitEntry, Benefit
from posot import OrderTakerException, OrderTaker

from ._SaleLine import SaleLine


class Order(object):
    """ Order's internal representation in the nDiscount component.
    """

    def __init__(self, obj, sale_lines=(), user_level=None, applied_benefits=()):
        self.id = int(obj.get("orderId")) if obj.get("orderId") else None
        total = (float(obj.get("totalAmount")) if obj.get("totalAmount") else 0) + \
                (float(obj.get("taxTotal")) if obj.get("taxTotal") else 0)
        self.total_amount = total
        self.pod_type = obj.get("podType")
        self.sale_lines = [SaleLine(o) for o in sale_lines]
        self.user_level = user_level
        self.pos_id = int(obj.get("posId"))
        self.applied_benefits = [
            AppliedBenefitEntry(
                    o["benefit"],
                    o["used_discount_ids"],
                    o["added_sale_lines"],
                    o["burnt_items"],
                    o["promotion_tender_amount"]
            )
            for o in applied_benefits
        ]

    @staticmethod
    def pre_serialize_applied_benefits(applied_benefits):
        # type: (list[AppliedBenefitEntry]) -> list
        return [
            {
                "benefit": loads(o.benefit.to_json()),
                "used_discount_ids": list(o.used_discount_ids),
                "added_sale_lines": list(o.added_sale_lines),
                "burnt_items": o.burnt_items,
                "promotion_tender_amount": o.promotion_tender_amount
            }
            for o in applied_benefits
        ]

    @staticmethod
    def get_burnt_items(order):
        # type: (Order) -> dict
        burnt_items = dict()
        for benefit in order.applied_benefits:
            for entry in benefit.burnt_items.items():
                burnt_items[entry[0]] = entry[1] \
                    if burnt_items.get(entry[0]) is None else (burnt_items.get(entry[0]) + entry[1])

        return burnt_items

    @staticmethod
    def get_used_discount_ids(posot):
        # type: (OrderTaker) -> list[int]
        try:
            order_discount_list = eTree.XML(posot.getOrderDiscounts(applied=True)).findall(".//OrderDiscount")
            return [int(el.get("discountId")) for el in order_discount_list if el.tag == "OrderDiscount"]
        except OrderTakerException:
            return []

    @staticmethod
    def get_available_discount_ids(posot):
        # type: (OrderTaker) -> set
        available_discount_ids = set(range(600, 700))
        discount_ids = set(Order.get_used_discount_ids(posot))
        return available_discount_ids.difference(discount_ids)

    @staticmethod
    def get_applied_benefits_json(order):
        # type: (Order) -> list[dict]
        return dumps([
            {
                "benefit": loads(o.benefit.to_json()),
                "used_discount_ids": list(o.used_discount_ids),
                "added_sale_lines": list(o.added_sale_lines),
                "burnt_items": o.burnt_items,
                "promotion_tender_amount": o.promotion_tender_amount
            }
            for o in order.applied_benefits
        ])

    @staticmethod
    def get_items_to_burn(order, benefit):
        # type: (Order, Benefit) -> dict
        """
        Returns a dict that maps sale lines + line level to its quantity to be burnt (or None).
        Indexing: '{sale_line}.{line_number}' -> burnt_quantity
        """
        sale_lines = order.sale_lines
        conditions = benefit.conditions
        burnt_items = Order.get_burnt_items(order)
        items_to_burn = dict()

        required_items_on_sale = {}

        for item in conditions.required_items_on_sale:
            key = "{};{}".format(item.context if item.context else 'any', str(item.item_id))
            required_items_on_sale[key] = item.quantity

        for sale_line in sale_lines:
            context = sale_line.context
            quantity = sale_line.qty

            quantity -= 0 if conditions.ignore_burned_items else int(burnt_items.get(sale_line.key, 0))

            for item_index in required_items_on_sale.keys():
                required_item_context, required_item_id = item_index.split(';')

                if int(sale_line.item_id) != int(required_item_id):
                    continue

                if required_item_context == 'any' or required_item_context in context:
                    t_quantity = quantity
                    quantity = max(0, quantity - required_items_on_sale[item_index])
                    required_items_on_sale[item_index] = max(0, required_items_on_sale[item_index] - t_quantity)

            items_to_burn[sale_line.key] = sale_line.qty - quantity

        for key in items_to_burn.keys():
            if items_to_burn.get(key, 0) == 0:
                items_to_burn.pop(key)
        return items_to_burn

    def to_json(self):
        return dumps(self, default=lambda o: o.__dict__ if hasattr(o, '__dict__') else str(o), sort_keys=True)
