class ChangeProdStateRequest(object):
    def __init__(self, order_id, view, state):
        # type: (int, str, str) -> None
        self.order_id = order_id
        self.view = view
        self.state = state
