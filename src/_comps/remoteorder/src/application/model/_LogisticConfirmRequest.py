class LogisticConfirmRequest:
    def __init__(self, remote_order_id, adapter_name, adapter_logistic_id):
        # type: (str, str, str) -> None
        
        self.remote_order_id = remote_order_id
        self.adapter_name = adapter_name
        self.adapter_logistic_id = adapter_logistic_id
