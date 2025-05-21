def check_and_remove(order_list, order, state_type, state_value, match=True):
    if order.order_id not in order_list:
        return

    if not order.items or (state_match(order, state_type, state_value) and match):
        order_list.remove(order.order_id)


def state_match(order, state_type, state_value):
    if state_type.lower() == "order_state":
        state_from_history = next((s for s in order.state_history if s.state == state_value), None)
        return (state_from_history.state == state_value) if state_from_history else False

    return order.prod_state == state_value
