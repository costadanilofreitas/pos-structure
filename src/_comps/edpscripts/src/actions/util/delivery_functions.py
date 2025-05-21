def is_delivery_order(model):
    order = model.find("CurrentOrder/Order")
    if not order:
        return False
    
    return order.find("CustomOrderProperties/OrderProperty[@key='REMOTE_ORDER_ID']") is not None
