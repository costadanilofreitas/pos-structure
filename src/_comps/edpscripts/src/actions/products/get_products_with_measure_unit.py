import persistence
from systools import sys_log_exception

from .. import mb_context


available_measure_unit = 'kg'
_products_with_measure_unit_cache = []


def get_products_with_measure_unit_cache(pos_id='1'):
    global _products_with_measure_unit_cache

    if not _products_with_measure_unit_cache:
        conn = None
        try:
            conn = persistence.Driver().open(mb_context, pos_id)
            query = "SELECT ProductCode FROM ProductKernelParams WHERE MeasureUnit = '{}'"\
                .format(available_measure_unit)
            cursor = conn.select(query)
            for row in cursor:
                product_code = row.get_entry(0)
                if product_code not in _products_with_measure_unit_cache:
                    _products_with_measure_unit_cache.append(product_code)

        except (persistence.AprException, persistence.DbdException) as _:
            sys_log_exception("Error getting products with measure unit")
        finally:
            if conn:
                conn.close()

    return _products_with_measure_unit_cache


def is_a_product_with_measure_unit(product_code):
    if str(product_code) in _products_with_measure_unit_cache:
        return True
    return False
