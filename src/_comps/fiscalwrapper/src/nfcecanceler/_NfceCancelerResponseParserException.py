class NfceCancelerResponseParserException(Exception, object):
    def __init__(self, message):
        super(NfceCancelerResponseParserException, self).__init__(message)
