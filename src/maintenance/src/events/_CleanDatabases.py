# -*- coding: utf-8 -*-

import logging
import os
import sqlite3
import subprocess

from msgbus import TK_POS_GETPOSLIST, TK_SYS_NAK, FM_PARAM
from persistence import Driver

logger = logging.getLogger("Maintenance")


class CleanDatabasesProcessor(object):
    def __init__(self, mbcontext, comp_no, days_to_keep_orders):
        self.mbcontext = mbcontext
        self.comp_no = comp_no
        self.days_to_keep_orders = days_to_keep_orders

        self.maintenance_processor = None
        self.pos_list = None

    def set_server_parameters(self, maintenance_processor):
        self.maintenance_processor = maintenance_processor

    def clean_databases(self):
        try:
            # Server
            if self.comp_no == 0:
                self.pos_list = self._get_pos_list()

                self._clean_orders_database()
                self._clean_fiscal_database()
            # POS
            else:
                return
        except Exception as _:
            logger.exception("Error cleaning databases")

    def vacuum_databases(self):
        try:
            # Server
            if self.comp_no == 0:
                self.pos_list = self._get_pos_list()

                self._vacuum_production_database()
                self._vacuum_fiscal_database()
                self._vacuum_orders_database()
            # POS
            else:
                return
        except Exception as _:
            logger.exception("Error doing vacuum on databases")

    def _clean_orders_database(self):
        logger.info("Starting [_clean_orders_database]")
        try:
            orders_stored_all_pos = []
            conn = None

            for pos_id in sorted(self.pos_list, key=lambda _: int(_)):
                try:
                    conn = Driver().open(self.mbcontext, service_name='Persistence', dbname=str(pos_id))

                    logger.info('Starting backup process for POS: %s' % pos_id)
                    try:
                        orders_stored = self._backup_orders(conn)
                        if orders_stored:
                            orders_stored_all_pos.extend(orders_stored)
                        else:
                            logger.info("Have no orders to clean in order db: {}".format(pos_id))
                    except Exception as _:
                        logger.exception("Error doing backup - POS: %s" % pos_id)
                        break
                finally:
                    if conn:
                        conn.close()

            if orders_stored_all_pos:
                for pos_id in self.pos_list:
                    try:
                        conn = Driver().open(self.mbcontext, service_name='Persistence', dbname=str(pos_id))
                        orders_stored_list = [orders_stored_all_pos[x:x + 100] for x in xrange(0, len(orders_stored_all_pos), 100)]
                        logger.info("Starting [_delete_orders] por POS: {}".format(pos_id))
                        for orders_stored in orders_stored_list:
                            self._delete_orders(conn, orders_stored)
                        logger.info("Finished [_delete_orders] por POS: {}".format(pos_id))
                    finally:
                        if conn:
                            conn.close()

            logger.info('Finished [_clean_orders_database]')
        except Exception as _:
            logger.exception("Error cleaning order dbs")

    def _vacuum_orders_database(self):
        # For each POS - Backup Orders DB
        logger.info("Starting [_vacuum_orders_database]")
        try:
            order_db_files = []
            conn = None

            for pos_id in sorted(self.pos_list, key=lambda _: int(_)):
                try:
                    conn = Driver().open(self.mbcontext, service_name='Persistence', dbname=str(pos_id))

                    order_db_files.append(self.get_db_file(conn, "orderdb"))
                finally:
                    if conn:
                        conn.close()

            for order_db in order_db_files:
                conn = None
                old_file_size = os.path.getsize(order_db)/1024/1024
                logger.info('Doing VACUUM for order db: {}'.format(order_db.split('db')[1]))

                try:
                    conn = sqlite3.connect(order_db)
                    conn.execute("VACUUM;")  # This will decrease the size of the databases
                except Exception as ex:
                    logger.exception("Error doing vacuum - %s - Message %s" % (order_db, str(ex)))
                    if conn is not None:
                        conn.close()
                else:
                    conn.close()

                new_file_size = os.path.getsize(order_db)/1024/1024

                logger.info('Order db file sizes. OLD: {}mb; NEW: {}mb'.format(old_file_size, new_file_size))

            logger.info('Finished [_vacuum_orders_database]')
        except Exception as _:
            logger.exception("Error doing vacuum on order dbs")

    @staticmethod
    def _delete_orders(conn, orders_stored):
        purge_sql = '''
                         DELETE FROM orderdb.OrderCustomProperties WHERE OrderId IN ({0});
                         DELETE FROM orderdb.OrderItemCustomProperties WHERE OrderId IN ({0});
                         DELETE FROM orderdb.OrderStateHistory WHERE OrderId IN ({0});
                         DELETE FROM orderdb.OrderItem WHERE OrderId IN ({0});
                         DELETE FROM orderdb.OrderTax WHERE OrderId IN ({0});
                         DELETE FROM orderdb.OrderDiscount WHERE OrderId IN ({0});
                         DELETE FROM orderdb.OrderVoidHistory WHERE OrderId IN ({0});
                         DELETE FROM orderdb.OrderTender WHERE OrderId IN ({0});
                         DELETE FROM orderdb.OrderComment WHERE OrderId IN ({0});
                         DELETE FROM orderdb.Orders WHERE OrderId IN ({0});
                     '''.format(','.join(orders_stored))

        try:
            execute_db_transaction(conn, purge_sql, close_conn=False)
        except Exception as _:
            logger.exception("Error purging database - ROLLBACK")

    def _backup_orders(self, conn):
        logger.info("Starting [_backup_orders]")
        orders_stored = []
        cursor = conn.select('''SELECT OrderId FROM orderdb.Orders
                               WHERE BusinessPeriod < strftime('%Y%m%d', 'now', '-{0} days')
                               AND StateId IN (SELECT StateId FROM orderdb.OrderState WHERE StateDescr IN ('PAID', 'VOIDED'))
                               ORDER BY OrderId LIMIT 500'''.format(self.days_to_keep_orders))
        order_list = map(lambda x: x.get_entry('OrderId'), cursor)

        if len(order_list) < 1:
            return

        backup_sql = '''
                         INSERT OR REPLACE INTO backuporders.Orders SELECT * FROM orderdb.Orders WHERE OrderId IN ({0});
                         INSERT OR REPLACE INTO backuporders.OrderCustomProperties SELECT * FROM orderdb.OrderCustomProperties WHERE OrderId IN ({0});
                         INSERT OR REPLACE INTO backuporders.OrderItemCustomProperties SELECT * FROM orderdb.OrderItemCustomProperties WHERE OrderId IN ({0});
                         INSERT OR REPLACE INTO backuporders.OrderStateHistory SELECT * FROM orderdb.OrderStateHistory WHERE OrderId IN ({0});
                         INSERT OR REPLACE INTO backuporders.OrderItem SELECT * FROM orderdb.OrderItem WHERE OrderId IN ({0});
                         INSERT OR REPLACE INTO backuporders.OrderTax SELECT * FROM orderdb.OrderTax WHERE OrderId IN ({0});
                         INSERT OR REPLACE INTO backuporders.OrderDiscount SELECT * FROM orderdb.OrderDiscount WHERE OrderId IN ({0});
                         INSERT OR REPLACE INTO backuporders.OrderVoidHistory SELECT * FROM orderdb.OrderVoidHistory WHERE OrderId IN ({0});
                         INSERT OR REPLACE INTO backuporders.OrderTender SELECT * FROM orderdb.OrderTender WHERE OrderId IN ({0});
                         INSERT OR REPLACE INTO backuporders.OrderComment SELECT * FROM orderdb.OrderComment WHERE OrderId IN ({0});
                     '''.format(','.join(order_list))
        try:
            execute_db_transaction(conn, backup_sql, close_conn=False)
            orders_stored = order_list
            logger.info("Finished [_backup_orders]")
        except Exception as _:
            logger.exception("Error doing backup - ROLLBACK")
        return orders_stored

    def _clean_fiscal_database(self):
        try:
            logger.info("Starting [_clean_fiscal_database]")

            conn = None
            try:
                conn = Driver().open(self.mbcontext, service_name="FiscalPersistence")

                logger.info('Starting purge of orders on fiscal database')
                orders_backup = self._backup_fiscal(conn)
                if orders_backup:
                    self._delete_fiscal(conn, orders_backup)
                else:
                    logger.info("Have no order to clean in fiscal db")
            except Exception as ex:
                if "malformed" in ex.message:
                    logger.exception("Malformed database. Executing hard clean")
                    db_file = self.get_db_file(conn, "fiscal")
                    self._hard_clean_fiscal_database(db_file)
                logger.exception('Error purging orders on fiscal database')
                raise ex
            else:
                logger.info('Finalized purge of orders on fiscal database')
            finally:
                if conn:
                    conn.close()

            logger.info("Finished [_clean_fiscal_database]")
        except Exception as _:
            logger.exception("Error cleaning fiscal db")

    def _vacuum_fiscal_database(self):
        try:
            logger.info("Starting [_vacuum_fiscal_database]")

            conn = None
            try:
                conn = Driver().open(self.mbcontext, service_name="FiscalPersistence")
                db_file = self.get_db_file(conn, "fiscal")
            except Exception as ex:
                if "malformed" in ex.message:
                    logger.exception("Malformed database. Executing hard clean")
                    db_file = self.get_db_file(conn, "fiscal")
                    self._hard_clean_fiscal_database(db_file)
                logger.exception('Error doing vacuum on fiscal database')
                raise ex
            finally:
                if conn:
                    conn.close()

            old_file_size = os.path.getsize(db_file) / 1024 / 1024
            conn = None
            try:
                logger.info('Doing VACUUM for fiscal database')
                if db_file:
                    conn = sqlite3.connect(db_file)
                    conn.execute("VACUUM;")
            except Exception as _:
                logger.exception('Error doing vacuum on fiscal db')
            finally:
                if conn:
                    conn.close()

            new_file_size = os.path.getsize(db_file) / 1024 / 1024

            logger.info('Fiscal db file sizes. OLD: {}mb; NEW: {}mb'.format(old_file_size, new_file_size))

            logger.info("Finished [_vacuum_fiscal_database]")
        except Exception as _:
            logger.exception("Error doing vacuum on fiscal db")

    def _vacuum_production_database(self):
        try:
            logger.info("Starting [_vacuum_production_database]")

            conn = None
            try:
                conn = Driver().open(self.mbcontext)
                db_file = self.get_db_file(conn, "production")
            finally:
                if conn:
                    conn.close()

            old_file_size = os.path.getsize(db_file) / 1024 / 1024
            conn = None
            try:
                logger.info('Doing VACUUM on production database')
                if db_file:
                    conn = sqlite3.connect(db_file)
                    conn.execute("VACUUM;")
            except Exception as _:
                logger.exception('Error doing vacuum on production database')
            finally:
                if conn:
                    conn.close()

            new_file_size = os.path.getsize(db_file) / 1024 / 1024

            logger.info('Production database file sizes. OLD: {}mb; NEW: {}mb'.format(old_file_size, new_file_size))

            logger.info("Finished [_vacuum_production_database]")
        except Exception as _:
            logger.exception("Error doing vacuum on production database")

    @staticmethod
    def get_db_file(conn, db_name_to_find):
        db_file = None
        pragma_cursor = conn.select("PRAGMA database_list;")
        for pragma_row in pragma_cursor:
            db_name, db_file = map(pragma_row.get_entry, (1, 2,))
            if db_name == db_name_to_find:
                break
        return db_file

    @staticmethod
    def _delete_fiscal(conn, orders_backup):
        logger.info("Starting [delete_fiscal]")
        purge_sql = """DELETE FROM fiscal.FiscalData WHERE OrderId in ('{0}');
                       DELETE FROM fiscal.PaymentData WHERE OrderId in ('{0}');"""
        try:
            execute_db_transaction(conn, purge_sql.format("','".join(orders_backup)), close_conn=False)
            logger.info("Finished [delete_fiscal]")
        except Exception as ex:
            logger.exception("Error purging order {0} on fiscal database")
            if "malformed" in ex.message:
                raise ex

    def _backup_fiscal(self, conn):
        logger.info("Starting [_backup_fiscal]")
        cursor = conn.select('''SELECT OrderId
                                FROM fiscal.FiscalData
                                WHERE SentToBKC = 1 AND SentToBKOffice = 1 AND SentToNfce = 1 AND strftime('%s', 'now', '-{0} days') > DataNota
                                ORDER BY OrderId LIMIT 500'''.format(self.days_to_keep_orders))
        order_list = map(lambda x: x.get_entry('OrderId'), cursor)
        if len(order_list) < 1:
            return

        backup_sql = """INSERT OR REPLACE INTO backupfiscal.PaymentData SELECT * FROM fiscal.PaymentData WHERE OrderId in ('{0}');
                        INSERT OR REPLACE INTO backupfiscal.FiscalData SELECT * FROM fiscal.FiscalData WHERE OrderId in ('{0}');"""

        execute_db_transaction(conn, backup_sql.format("','".join(order_list)), close_conn=False)
        logger.info("Finished [_backup_fiscal]")
        return order_list

    def _get_pos_list(self):
        try:
            pos_list = []
            msg = self.mbcontext.MB_EasySendMessage('PosController', TK_POS_GETPOSLIST, FM_PARAM)
            if msg.token == TK_SYS_NAK or not msg.data:
                raise
            for pos_id in msg.data.split('\0'):
                if pos_id not in pos_list:
                    pos_list.append(pos_id)
            return sorted(pos_list)
        except Exception:
            logger.exception("Error getting the list of POS")

    @staticmethod
    def _hard_clean_fiscal_database(db_file):
        logger.info("Starting [_hard_clean_fiscal_database]")
        subprocess.call(["sqlite3",
                         db_file,
                         ".mode insert",
                         ".output dump_all.sql",
                         ".dump",
                         ".read dump_all.sql"], shell=True)
        logger.info("Finished [_hard_clean_fiscal_database]")


def execute_db_transaction(conn, query, close_conn=True):
    try:
        conn.transaction_start()
        conn.query('''BEGIN TRANSACTION;''')
        conn.query(query)
    except Exception as ex:
        conn.query('''ROLLBACK TRANSACTION;''')
        raise ex
    else:
        conn.query('''COMMIT TRANSACTION;''')
    finally:
        if close_conn:
            conn.close()
