class Action(object):
    def __init__(self, obj):
        self.order = int(obj.get("order")) if obj.get("order") else None
        self.name = obj.get("name")
        self.value = obj.get("value")
