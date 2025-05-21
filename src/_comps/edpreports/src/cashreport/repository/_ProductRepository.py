from unicodedata import normalize

from old_helper import BaseRepository

tender_types_cash = {}
grouped_tender_types = {}


class ProductRepository(BaseRepository):
    def __init__(self, mbcontext):
        super(ProductRepository, self).__init__(mbcontext)

    def populate_card_brands_groups(self, card_brands_payments):
        if len(tender_types_cash) == 0:
            self._get_tender_types()
            self._group_card_brands()

        populated_brands = {}
        for tender_id in card_brands_payments:
            tender_name = self.get_tender_name(tender_id).title()

            card_brand = {tender_name: {'value': card_brands_payments[tender_id]['value'],
                                        'quantity': card_brands_payments[tender_id]['quantity'],
                                        'id': tender_id}}

            if tender_id in grouped_tender_types:
                if tender_name in populated_brands:
                    populated_brands[tender_name].update(card_brand)
                else:
                    populated_brands[tender_name] = card_brand
            else:
                parent_id = self.get_parent_id(tender_id)
                parent_name = self.get_tender_name(parent_id).title()
                if parent_name in populated_brands:
                    parent_brands = populated_brands[parent_name]
                    if tender_name in parent_brands:
                        parent_brands[tender_name]['value'] += card_brands_payments[tender_id]['value']
                        parent_brands[tender_name]['quantity'] += card_brands_payments[tender_id]['quantity']
                    else:
                        parent_brands.update(card_brand)
                else:
                    populated_brands[parent_name] = card_brand

        from collections import OrderedDict
        for tender in populated_brands:
            populated_brands[tender] = OrderedDict(sorted(populated_brands[tender].items()))
        return OrderedDict(sorted(populated_brands.items()))

    @staticmethod
    def get_tender_name(tender_id):
        if tender_id in tender_types_cash:
            return _remove_accents(tender_types_cash[tender_id][0])
        return "OUTROS"

    @staticmethod
    def get_parent_id(tender_id):
        for parent_id in grouped_tender_types:
            if tender_id in grouped_tender_types[parent_id]:
                return parent_id

    @staticmethod
    def _group_card_brands():
        for tender_id in tender_types_cash:
            tender_parent_id = tender_types_cash[tender_id][1]
            if tender_parent_id is not None:
                if int(tender_parent_id) in grouped_tender_types:
                    grouped_tender_types[int(tender_parent_id)].append(tender_id)
                else:
                    grouped_tender_types[int(tender_parent_id)] = [tender_id]
            else:
                if tender_id not in grouped_tender_types:
                    grouped_tender_types[tender_id] = []

    def _get_tender_types(self):
        def inner_func(conn):
            query = _GetTenderTypes
            cursor = conn.select(query)
            for row in cursor:
                tender_types_cash[int(row.get_entry(0))] = (str(row.get_entry(1)), row.get_entry(2))

        return self.execute_with_connection(inner_func)


_GetTenderTypes = "SELECT TenderId, TenderDescr, ParentTenderId FROM TenderType"


def _remove_accents(text):
    return normalize('NFKD', unicode(text.decode("utf8"))).encode('ASCII', 'ignore')
