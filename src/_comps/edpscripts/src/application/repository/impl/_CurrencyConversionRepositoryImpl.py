from application.repository import CurrencyConversionRepository


class CurrencyConversionRepositoryImpl(CurrencyConversionRepository):
    def get_currency_exchange(self):

        def inner_func(conn):
            rate_amount_list = conn.select(
                """
                    select RateAmount
                    from CurrencyExchange
                    where CurrencyFrom = 'BRL' and
                    CurrencyTo = 'USD' and
                    date('now') >= ValidFrom and
                    date('now') < ValidThru
                """)

            rate_amount_list = [float(x.get_entry(0)) for x in rate_amount_list]
            return rate_amount_list[0]

        return self.execute_with_connection(inner_func)
