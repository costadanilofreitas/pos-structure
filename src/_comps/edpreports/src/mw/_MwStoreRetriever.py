from domain import StoreRetriever, Store
from old_helper import read_swconfig


class MwStoreRetriever(StoreRetriever):
    def __init__(self, mbcontext):
        self.mbcontext = mbcontext

    def get_store(self):
        code = read_swconfig(self.mbcontext, "Store.Id")
        return Store(code)
