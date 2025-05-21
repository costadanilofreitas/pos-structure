class InvalidResponseCode(Exception):
    def __init__(self, response_code):
        self.response_code = response_code
