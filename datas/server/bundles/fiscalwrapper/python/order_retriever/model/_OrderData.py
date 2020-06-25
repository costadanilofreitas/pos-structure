class OrderData(object):
    def __init__(self, order_id, pos_id, order_picture, order_xml):
        # type: (int, int, unicode, unicode) -> None
        self.order_id = order_id
        self.pos_id = pos_id
        self.order_picture = order_picture
        self.order_xml = order_xml
