import iso8601


def get_order_timestamp(order, state_type, state_value):
    if state_type.lower() == "order_state":
        state = next((s for s in order.state_history if s.state == state_value), None)
        return iso8601.parse_date(state.timestamp)

    return iso8601.parse_date(order.prod_state_last_update)
