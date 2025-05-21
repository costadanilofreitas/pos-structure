# -*- coding: utf-8 -*-

import inspect
import time

from datetime import datetime
from logging import Logger

from mw_helper import BaseRepository
from msgbus import MBEasyContext
from model import RuptureItem


class RuptureRepository(BaseRepository):
    def __init__(self, mb_context, logger):
        # type: (MBEasyContext, Logger) -> None
        super(RuptureRepository, self).__init__(mb_context)

        self.logger = logger

    def __getattribute__(self, name):
        returned = object.__getattribute__(self, name)
        if inspect.isfunction(returned) \
                or inspect.ismethod(returned) \
                and returned.__name__ != "execute_with_connection":
            self.logger.info("[RuptureRepository] Call -> {}".format(returned.__name__))
        return returned

    def get_disabled_items(self):
        def inner_func(conn):
            cursor = conn.select("""
                SELECT DISTINCT
                    ri.ProductCode,
                    p.ProductName,
                    pp.ProductCode AS ProductPartCode
                FROM
                    RupturaItens ri
                    LEFT JOIN Product p ON p.ProductCode = ri.productCode
                    LEFT JOIN ProductPart pp ON pp.PartCode = p.ProductCode
                WHERE
                    EnableDate IS NULL
            """)

            items = []
            for x in cursor:
                product_code = x.get_entry("ProductCode")
                product_name = x.get_entry("ProductName")
                product_part_code = x.get_entry("ProductPartCode")
                rupture_item = RuptureItem(product_code, product_name, product_part_code)
                items.append(rupture_item)

            return items

        return self.execute_with_connection(inner_func)

    def get_enabled_items(self):
        def inner_func(conn):
            cursor = conn.select("""
                SELECT DISTINCT
                    p.ProductCode,
                    p.ProductName,
                    pp.ProductCode AS ProductPartCode
                FROM 
                    ProductKernelParams pkp
                    INNER JOIN Product p ON p.ProductCode = pkp.ProductCode
                    LEFT JOIN RupturaItens ri ON ri.ProductCode = pkp.ProductCode
                    LEFT JOIN ProductPart pp ON pp.PartCode = p.ProductCode
                WHERE pkp.ProductType in (0, 2) AND
                    p.ProductCode NOT IN (SELECT ProductCode FROM RupturaItens WHERE EnableDate IS NULL)
            """)

            items = []
            for x in cursor:
                product_code = x.get_entry("ProductCode")
                product_name = x.get_entry("ProductName")
                product_part_code = x.get_entry("ProductPartCode")
                rupture_item = RuptureItem(product_code, product_name, product_part_code)
                items.append(rupture_item)

            return items

        return self.execute_with_connection(inner_func)

    def insert_rupture_update(self, session_id, items_to_disable, items_to_enable, disabled_items):
        def inner_func(conn):
            query = ""
            query += self.fill_items_to_disable(session_id, items_to_disable, disabled_items)
            query += self.fill_items_to_enable(session_id, items_to_enable)

            if not query:
                return

            conn.query(query)

        self.execute_with_connection(inner_func)

    def insert_rupture_snapshot(self, disabled_items):
        def inner_func(conn):
            inactive_list = ",".join(disabled_items)
            snapshot_id = self._get_new_snapshot_id()

            query = """INSERT INTO RupturaSnapshot (ID, InactiveProdList) VALUES ('{}','{}');"""
            conn.query(query.format(snapshot_id, inactive_list))
            return snapshot_id

        return self.execute_with_connection(inner_func)

    def insert_rupture_current_state(self, snapshot_id):
        def inner_func(conn):
            query = """INSERT INTO RupturaCurrentState VALUES ('{}', 'Delivery', '999');"""
            conn.query(query.format(snapshot_id))

        self.execute_with_connection(inner_func)

    def insert_event_state(self, event_data):
        def inner_func(conn):
            query = """INSERT OR REPLACE INTO CleanRuptureEvent VALUES ('{}', 0);"""
            conn.query(query.format(event_data))

        self.execute_with_connection(inner_func)

    def check_if_need_to_clean_ruptures(self):
        def inner_func(conn):
            query = """SELECT * FROM CleanRuptureEvent WHERE Processed = 0;"""
            return [row.get_entry(0) for row in conn.select(query)]

        return self.execute_with_connection(inner_func)

    def mark_clean_rupture_event_as_processed(self):
        def inner_func(conn):
            conn.query("""UPDATE CleanRuptureEvent SET Processed = 1;""")

        self.execute_with_connection(inner_func)

    def mark_pending_ruptures_as_processed(self):
        def inner_func(conn):
            conn.query("""UPDATE RupturaCurrentState
                          SET Processed = 1
                          WHERE Environment = 'Delivery'
                            AND Processed <> 1;""")

        self.execute_with_connection(inner_func)

    def clean_rupture_items(self):
        def inner_func(conn):
            conn.query("""UPDATE RupturaItens 
                          SET EnableDate=DATETIME('NOW'), EnableSessionId='AUTO_CLEAN_EVENT'
                          WHERE EnableDate IS NULL;""")

        self.execute_with_connection(inner_func)

    def clean_rupture_items_by_btn(self, enable_session_id):
        def inner_func(conn):
            conn.query("""UPDATE RupturaItens 
                          SET EnableDate=DATETIME('NOW'), EnableSessionId='{}' 
                          WHERE EnableDate IS NULL;"""
                       .format(enable_session_id))

        self.execute_with_connection(inner_func)

    @staticmethod
    def fill_items_to_disable(session_id, items_to_disable, disabled_items):
        query = ""
        if items_to_disable:
            disabled_list = list(disabled_items.iterkeys())
            filtered_items = set(map(lambda y: y['product_code'], items_to_disable)).difference(disabled_list)
            filtered_items_to_disable = list(z for z in items_to_disable if z['product_code'] in filtered_items)

            if len(filtered_items_to_disable) > 0:
                query += "INSERT INTO RupturaItens (ProductCode, Period, SessionId) VALUES "
                for item in filtered_items_to_disable:
                    query += "('{0}', DATETIME('NOW'), '{1}'),".format(item.get('product_code'), session_id)
                query = query[:-1] + ";"

        return query

    @staticmethod
    def fill_items_to_enable(session_id, items_to_enable):
        query = ""
        if items_to_enable:
            query += """
                        UPDATE RupturaItens
                        SET EnableDate=DATETIME('NOW'), EnableSessionId='{0}'
                        WHERE ProductCode IN ({1}) AND
                            EnableDate IS NULL AND
                            EnableSessionId IS NULL;
                     """.format(session_id, ",".join([x['product_code'] for x in items_to_enable]))

        return query

    @staticmethod
    def _get_new_snapshot_id():
        return int(time.mktime(datetime.now().timetuple()))
