class NfceDisablerResponseException(Exception, object):
    def __init__(self, response):
        super(NfceDisablerResponseException, self).__init__(response)
        self.response = response
