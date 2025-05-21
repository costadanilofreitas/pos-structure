class LogisticCancelRequest:
    def __init__(self, logistic_id, store_id):
        # type: (str, str) -> None
        
        self.logistic_id = logistic_id
        self.store_id = store_id
        self.reason = "Order Canceled"
