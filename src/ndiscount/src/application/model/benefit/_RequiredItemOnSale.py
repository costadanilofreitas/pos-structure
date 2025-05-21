class RequiredItemOnSale(object):
    def __init__(self, obj):
        self.item_id = int(obj.get("item")) if obj.get("item") else None
        self.item_id = int(obj.get("item_id")) if obj.get("item_id") and self.item_id is None else self.item_id
        self.context = obj.get("context")
        self.quantity = int(obj.get("quantity")) if obj.get("quantity") else None
