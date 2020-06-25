class OrderRetrieverException(Exception):
    def __init__(self, error_message):
        super(OrderRetrieverException, self).__init__(error_message)
