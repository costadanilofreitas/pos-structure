# -*- coding: utf-8 -*-

import logging
import logging.config
import logging.handlers
import os
import re
import sqlite3
import sys
from StringIO import StringIO
from abc import ABCMeta
from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from xml.etree import cElementTree as eTree

import six
from dateutil import tz
from msgbus import FM_PARAM, TK_SYS_NAK, TK_STORECFG_GET, TK_POS_GETPOSLIST, MBEasyContext
from persistence import Driver, Connection, DbdException
from typing import Callable, Any, List, Optional, Union


def F(value):
    if value is None:
        return 0
    return float(value)
# END F


def get_sale_line_priced_items(sale_lines, ignore_price=False):
    deleted_line_numbers = map(lambda x: x.get("lineNumber"), filter(lambda x: x.get("level") == "0" and x.get("qty") == "0", sale_lines))
    if ignore_price:
        active_sale_lines = filter(lambda x: (x.get("lineNumber") not in deleted_line_numbers), sale_lines)
    else:
        active_sale_lines = filter(lambda x: (x.get("lineNumber") not in deleted_line_numbers) and (F(x.get("itemPrice")) != 0), sale_lines)

    for sale_line in active_sale_lines:
        item_price, unit_price, item_qty, added_price, added_qty, multiplied_qty, inc_qty, level = map(sale_line.get, (("itemPrice", "unitPrice", "qty", "addedUnitPrice", "addedQty", "multipliedQty", "incQty", "level")))
        item_discount = F(sale_line.get('itemDiscount'))
        unit_price_cache = F(sale_line.get("addedUnitPrice")) or F(sale_line.get("unitPrice"))
        try:
            if F(unit_price) > 0:
                if F(item_price)/F(unit_price) != F(item_qty):
                    unit_price_cache = F(item_price) / F(item_qty)
                    unit_price = unit_price_cache
        except ZeroDivisionError:
            unit_price = 0
        try:
            correct_price = (F(unit_price) * F(item_qty) + F(added_price) * F(added_qty or item_qty)) * (F(multiplied_qty) / F(item_qty))

        except ZeroDivisionError:
            correct_price = 0

        unit_price = unit_price_cache
        if unit_price == 0 and F(item_price) > 0:
            unit_price = F(item_price) / F(item_qty)
            correct_price = F(item_price)
        try:
            item_qty = correct_price / unit_price
        except:
            item_qty = 0
        if not ignore_price:
            item_discount = (item_discount * (correct_price / F(item_price)))
            item_net_price = correct_price - item_discount
            item_price = correct_price

            sale_line.set("correctItemPrice", str(item_price))
            sale_line.set("correctItemNetPrice", str(item_net_price))
            sale_line.set("correctItemDiscount", str(item_discount))
        sale_line.set("correctQty", str(float(item_qty)))
        sale_line.set("correctUnitPrice", str(unit_price))

    return active_sale_lines
# END get_sale_line_priced_items


def read_swconfig(mbcontext, key):
    rmsg = mbcontext.MB_EasySendMessage("StoreWideConfig", token=TK_STORECFG_GET, format=FM_PARAM, data=key)
    if rmsg.token == TK_SYS_NAK:
        return None

    return str(rmsg.data)
# END read_swconfig


def get_log_file_path(loader_path, log_name='log.conf'):
    dir_path = os.path.dirname(os.path.realpath(loader_path))
    return os.path.join(dir_path, log_name)
# END get_log_file_path


def round_half_away_from_zero(number, precision=0):
    number = Decimal(number)
    value = number.quantize(Decimal('10') ** -(precision + 2))
    return float(value.quantize(Decimal('10') ** -precision, rounding=ROUND_HALF_UP))


def config_logger(loader_path, log_name='component'):
    dir_path = os.path.dirname(os.path.realpath(loader_path))
    filename = os.path.join(dir_path, log_name + '.log')

    formatter = logging.Formatter('%(asctime)-6s: %(name)s - %(levelname)s - %(thread)6d - %(threadName)-12s - %(message)s')

    rotating_file_logger = logging.handlers.RotatingFileHandler(filename, 'a', 5242880, 5)
    rotating_file_logger.setLevel(logging.DEBUG)  # DEBUG Log
    # rotating_file_logger.setLevel(logging.ERROR)  # Production Log
    rotating_file_logger.setFormatter(formatter)

    comp_logger = logging.getLogger(log_name)
    comp_logger.addHandler(rotating_file_logger)
    comp_logger.setLevel(logging.NOTSET)

    console_logger = logging.StreamHandler(sys.stdout)
    console_logger.setLevel(logging.ERROR)
    console_logger.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(console_logger)
    root_logger.setLevel(logging.NOTSET)
# END get_log_file_path


class OrderTaker(object):
    def __init__(self):
        pass

    def get_order_picture(self, pos_id, order_id=None):
        from sysactions import get_model, get_posot
        model = get_model(pos_id)
        posot = get_posot(model)
        if order_id is None:
            order = posot.orderPicture(pos_id)
            orders_xml = eTree.XML(order)

            return eTree.tostring(orders_xml)
        else:
            orders = posot.orderPicture(orderid=order_id)
            orders_xml = eTree.XML(orders)
            order = orders_xml.find("Order")

            return eTree.tostring(order)


class PosUtil(object):
    def __init__(self, mbcontext):
        self.mbcontext = mbcontext

    def get_pos_list(self):
        msg = self.mbcontext.MB_EasySendMessage("PosController", TK_POS_GETPOSLIST)
        if msg.token == TK_SYS_NAK:
            raise Exception("Could not retrieve PosList")

        pos_list = sorted(map(int, msg.data.split("\0")))

        return pos_list


def convert_from_utf_to_localtime(utc):
    # type: (datetime) -> datetime
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    # Tell the datetime object that it's in UTC time zone since
    # datetime objects are 'naive' by default
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    localtime = utc.astimezone(to_zone)

    return localtime


def convert_from_localtime_to_utc(localtime):
    # type: (datetime) -> datetime
    from_zone = tz.tzlocal()
    to_zone = tz.tzutc()

    # Tell the datetime object that it's in UTC time zone since
    # datetime objects are 'naive' by default
    localtime = localtime.replace(tzinfo=from_zone)

    # Convert time zone
    utc = localtime.astimezone(to_zone)

    return utc


def validar_cpf(cpf):
    """
    Valida CPFs, retornando apenas a string de números válida.

    # CPFs errados
    >>> validar_cpf('abcdefghijk')
    False
    >>> validar_cpf('123')
    False
    >>> validar_cpf('')
    False
    >>> validar_cpf(None)
    False
    >>> validar_cpf('12345678900')
    False

    # CPFs corretos
    >>> validar_cpf('95524361503')
    '95524361503'
    >>> validar_cpf('955.243.615-03')
    '95524361503'
    >>> validar_cpf('  955 243 615 03  ')
    '95524361503'
    """
    cpf = ''.join(re.findall('\d', str(cpf)))

    if (not cpf) or (len(cpf) < 11):
        return False

    # Pega apenas os 9 primeiros dígitos do CPF e gera os 2 dígitos que faltam
    inteiros = map(int, cpf)
    novo = inteiros[:9]

    while len(novo) < 11:
        r = sum([(len(novo) + 1 - i) * v for i, v in enumerate(novo)]) % 11

        if r > 1:
            f = 11 - r
        else:
            f = 0
        novo.append(f)

    # Se o número gerado coincidir com o número original, é válido
    if novo == inteiros:
        return cpf

    return False


def validar_cnpj(cnpj):
    """
    Valida CNPJs, retornando apenas a string de números válida.

    # CNPJs errados
    >>> validar_cnpj('abcdefghijklmn')
    False
    >>> validar_cnpj('123')
    False
    >>> validar_cnpj('')
    False
    >>> validar_cnpj(None)
    False
    >>> validar_cnpj('12345678901234')
    False
    >>> validar_cnpj('11222333000100')
    False

    # CNPJs corretos
    >>> validar_cnpj('11222333000181')
    '11222333000181'
    >>> validar_cnpj('11.222.333/0001-81')
    '11222333000181'
    >>> validar_cnpj('  11 222 333 0001 81  ')
    '11222333000181'
    """
    cnpj = ''.join(re.findall('\d', str(cnpj)))

    if (not cnpj) or (len(cnpj) < 14):
        return False

    # Pega apenas os 12 primeiros dígitos do CNPJ e gera os 2 dígitos que faltam
    inteiros = map(int, cnpj)
    novo = inteiros[:12]

    prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    while len(novo) < 14:
        r = sum([x * y for (x, y) in zip(novo, prod)]) % 11
        if r > 1:
            f = 11 - r
        else:
            f = 0
        novo.append(f)
        prod.insert(0, 6)

    # Se o número gerado coincidir com o número original, é válido
    if novo == inteiros:
        return cnpj

    return False


def regex_search(re_search, text, key=None):
    # type: (str, unicode, Optional[str]) -> Union[str, None]
    if key:
        re_search = re_search.format(key)
    result = re.search(re_search, text)
    if result not in (None, ""):
        return result.group(1)
    else:
        return None


def remove_xml_namespace(xml):
    # type: (Union[str, unicode]) -> eTree
    it = eTree.iterparse(StringIO(xml))
    for _, el in it:
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[1]
    return it.root


class Clock(object):
    def get_current_date(self):
        # type: () -> datetime
        pass

    def get_current_time(self):
        # type: () -> datetime
        pass


class RealClock(Clock):
    def get_current_time(self):
        return datetime.today()

    def get_current_date(self):
        return datetime.now().date()


class BaseRepository(object):
    __metaclass__ = ABCMeta

    def __init__(self, mbcontext):
        # type: (MBEasyContext) -> None
        self.mbcontext = mbcontext

    def execute_with_connection(self, method, db_name=None, service_name=None):
        # type: (Callable[[Connection], Any], str, str) -> Any
        conn = None
        try:
            conn = Driver().open(self.mbcontext, dbname=str(db_name) if db_name is not None else None, service_name=service_name)
            return method(conn)
        finally:
            if conn is not None:
                conn.close()

    def execute_with_transaction(self, method, db_name=None, service_name=None):
        # type: (Callable[[Connection], Any], str, str) -> Any
        def transaction_method(conn):
            # type: (Connection) -> Any

            if conn.get_number_of_instances() != 1 and db_name is None:
                raise DbdException("Cannot open transaction without DB instante")

            conn.transaction_start()
            try:
                conn.query("BEGIN TRANSACTION")
                ret = method(conn)
                conn.query("COMMIT")
                return ret
            except:
                conn.query("ROLLBACK")
                raise
            finally:
                conn.transaction_end()

        return self.execute_with_connection(transaction_method, db_name=db_name, service_name=service_name)

    def execute_in_all_databases(self, method, pos_list):
        # type: (Callable[[Connection], Any], List[int]) -> Any
        ret = []
        for pos in pos_list:
            conn = None
            try:
                conn = Driver().open(self.mbcontext, dbname=str(pos))
                ret.append(method(conn))
            finally:
                if conn is not None:
                    conn.close()

        return ret

    def execute_in_all_databases_returning_flat_list(self, method, pos_list):
        # type: (Callable[[Connection], Any], List[int]) -> Any
        inner_ret = self.execute_in_all_databases(method, pos_list)

        ret = []
        for inner_list in inner_ret:
            ret.extend(inner_list)

        return ret


class SQLiteBaseRepository(object):
    __metaclass__ = ABCMeta

    def __init__(self, db_path):
        # type: (unicode) -> None
        self.db_path = db_path

    def execute_with_connection(self, method):
        # type: (Callable[[sqlite3.Cursor], Any]) -> Any
        conn = None
        cursor = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            return method(cursor)
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def execute_with_transaction(self, method):
        # type: (Callable[[sqlite3.Cursor], Any]) -> Any
        conn = None
        cursor = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            ret = method(cursor)
            conn.commit()
            return ret
        except:
            conn.rollback()
            six.reraise(*sys.exc_info())
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()


class ValidationException(Exception):
    def __init__(self, error_code, localized_error_message):
        # type: (unicode, unicode) -> None
        self.error_code = error_code
        self.localized_error_message = localized_error_message

    def __str__(self):
        # type: () -> unicode
        return unicode(str(type(self))) + self.error_code + u": " + self.localized_error_message

    def __repr__(self):
        # type: () -> unicode
        return self.__str__()


class InvalidJsonException(Exception):
    def __init__(self, message, invalid_json=None):
        # type: (unicode, unicode) -> None
        self.message = message
        self.invalid_json = invalid_json

    def __str__(self):
        # type: () -> unicode
        return u"InvalidJsonException: " + self.message + u" " + self.invalid_json

    def __repr__(self):
        # type: () -> unicode
        return self.__str__()


def get_date_difference_GMT_timezone(timestamp):
    date_sangria = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    date_sangria = date_sangria.replace(tzinfo=tz.tzlocal())
    adjust_hours = int(date_sangria.strftime("%z")[2:][:1])
    date_sangria = date_sangria - timedelta(hours=adjust_hours)

    return date_sangria.strftime("%Y-%m-%dT%H:%M:%S%z")


def get_class_by_name(kls):
    # type: (unicode) -> type
    parts = kls.split(".")
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m
