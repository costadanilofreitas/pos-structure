from abc import abstractmethod, ABCMeta


class FiscalProcessor(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.total_taxes = {}

    @abstractmethod
    def terminate(self):
        pass

    @abstractmethod
    def request_fiscal(self, posid, order, tenders, paf=False):
        pass

    @abstractmethod
    def do_validation(self, get_days_to_expiration=None):
        pass

