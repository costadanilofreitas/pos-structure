from abc import ABCMeta, abstractmethod


class TransactionManager(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def begin_transaction(self):
        raise NotImplementedError()

    @abstractmethod
    def commit(self):
        raise NotImplementedError()

    @abstractmethod
    def rollback(self):
        raise NotImplementedError()


class UnitOfWork(object):
    __metaclass__ = ABCMeta

    def __init__(self, transaction_manager):
        # type: (TransactionManager) -> None
        self.transaction_manager = transaction_manager

    def with_transaction(self, method):
        try:
            self.transaction_manager.begin_transaction()
            ret = method()
            self.transaction_manager.commit()
            return ret
        except:
            self.transaction_manager.rollback()
            raise
