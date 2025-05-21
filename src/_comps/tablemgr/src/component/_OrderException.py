class OrderException(Exception):
    def __init__(self, code, message):
        super(OrderException, self).__init__(message)
        self.code = code

    def get_code(self):
        return self.code
