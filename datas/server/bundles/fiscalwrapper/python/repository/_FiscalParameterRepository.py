from old_helper import BaseRepository
from msgbus import MBEasyContext
from persistence import Connection


class FiscalParameterRepository(BaseRepository):
    def __init__(self, mbcontext):
        # type: (MBEasyContext) -> None
        super(FiscalParameterRepository, self).__init__(mbcontext)

    def get_fiscal_parameters(self):
        def inner_func(conn):
            # type: (Connection) -> Dict[Tuple[int, unicode], unicode]
            fiscal_parameters = {}
            for x in conn.select("select ProductCode, ParamName, ParamValue from FiscalParameter"):
                if x.get_entry(2) is not None and x.get_entry(2).lower() not in ('null', ''):
                    fiscal_parameters[(int(x.get_entry(0)), x.get_entry(1))] = x.get_entry(2)
            return fiscal_parameters

        return self.execute_with_connection(inner_func, service_name="FiscalPersistence")
