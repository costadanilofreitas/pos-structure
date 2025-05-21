from json import dumps


class SaleLine(object):
    def __init__(self, obj):
        self.qty = int(obj.get("qty")) if obj.get("qty") else 0
        self.context = obj.get("itemId")
        self.item_id = obj.get("partCode")
        self.item_price = float(obj.get("itemPrice")) if obj.get("itemPrice") else 0
        self.unit_price = float(obj.get("unitPrice")) if obj.get("unitPrice") else 0
        self.level = obj.get("level")
        self.line_number = obj.get("lineNumber")
        self.key = "{}.{}.{}.{}".format(self.line_number, self.level, self.context, self.item_id)

    def to_json(self):
        return dumps(self, default=lambda o: o.__dict__ if hasattr(o, '__dict__') else str(o), sort_keys=True)
