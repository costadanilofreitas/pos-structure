import re
from datetime import datetime

from dateutil.tz import tzutc, tzlocal
from msgbus import TK_SYS_NAK, TK_STORECFG_GET, FM_PARAM


def read_sw_config(mb_context, key):
    msg = mb_context.MB_EasySendMessage("StoreWideConfig", token=TK_STORECFG_GET, format=FM_PARAM, data=key)
    if msg.token == TK_SYS_NAK:
        return None

    return str(msg.data)


def validate_cpf(cpf):
    cpf = ''.join(re.findall('\d', str(cpf)))

    if (not cpf) or (len(cpf) < 11):
        return False

    integers = map(int, cpf)
    new = integers[:9]

    while len(new) < 11:
        r = sum([(len(new) + 1 - i) * v for i, v in enumerate(new)]) % 11

        if r > 1:
            f = 11 - r
        else:
            f = 0
        new.append(f)

    if new == integers:
        return cpf

    return False


def validate_cnpj(cnpj):
    cnpj = ''.join(re.findall('\d', str(cnpj)))

    if (not cnpj) or (len(cnpj) < 14):
        return False

    integers = map(int, cnpj)
    new = integers[:12]

    prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    while len(new) < 14:
        r = sum([x * y for (x, y) in zip(new, prod)]) % 11
        if r > 1:
            f = 11 - r
        else:
            f = 0
        new.append(f)
        prod.insert(0, 6)

    if new == integers:
        return cnpj

    return False


def convert_from_utf_to_localtime(utc):
    # type: (datetime) -> datetime

    from_zone = tzutc()
    to_zone = tzlocal()

    utc = utc.replace(tzinfo=from_zone)
    localtime = utc.astimezone(to_zone)

    return localtime
