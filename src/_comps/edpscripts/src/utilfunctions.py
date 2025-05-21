# -*- coding: utf-8 -*-
import json
import os
import re
from typing import Dict

import cfgtools
from sysactions import show_any_dialog, show_keyboard, StopAction, show_messagebox

from actions.config import get_customer_info_config


def get_void_reason(pos_id, selected_index=None):
    void_reason_ids = range(1, 13)
    void_reason_options = ["1 - Mudou de Ideia",
                           "2 - Duplicado",
                           "3 - Venda Errada",
                           "4 - Cancelamento",
                           "5 - Cupom Cancelado",
                           "6 - Pagamento Cancelado",
                           "7 - Pedido Salvo Cancelado",
                           "8 - Erro ao criar nova venda",
                           "9 - Erro ao processar pagamento",
                           "10 - Cancelamento via sistema",
                           "11 - Erro de sincronização",
                           "12 - Cancelamento com autorização do gerente"]
    void_reason_to_show = void_reason_options[0:4]
    if not selected_index:
        selected_index = show_any_dialog(pos_id, "filteredListBox", "", "$SELECT_REASON", "|".join(void_reason_to_show),
                                         "", "", 600000, "NOFILTER", "", "", "", None, False)

    if selected_index is None:
        return None

    selected_index = int(selected_index)
    void_reason_id = void_reason_ids[int(selected_index)]
    void_reason_descr = void_reason_options[int(selected_index)]
    void_reason_dict = {'VOID_REASON_ID': void_reason_id, 'VOID_REASON_DESCR': void_reason_descr}
    return void_reason_dict


def update_custom_properties(customer_doc=None, customer_name=None, pre_sale=None):
    dict_sale = {}

    if customer_doc not in (None, ""):
        dict_sale.update({"CUSTOMER_DOC": customer_doc})
    if customer_name not in (None, ""):
        dict_sale.update({"CUSTOMER_NAME": customer_name})
    if pre_sale not in (None, ""):
        dict_sale.update({"PRE_VENDA": pre_sale})

    return dict_sale


def get_customer_doc_after_paid(pos_id, pos_ot):
    config = cfgtools.read(os.environ["LOADERCFG"])
    customer_info_config = get_customer_info_config(pos_id)

    if "afterPaid" not in customer_info_config['document']:
        return ""

    valid = False
    customer_doc = ""
    while not valid:
        customer_doc = show_keyboard(pos_id, "$ONLY_NUMBER", "$ENTER_CPF_CNPJ", mask="CPF_CNPJ", numpad=True)
        if customer_doc is None:
            return None

        if customer_doc == "":
            ret = show_messagebox(pos_id, "$CONFIRM_EMPTY_CPF_CNPJ", buttons="$YES|$NO")
            if ret == 1:
                continue
            break
        customer_doc = str(customer_doc)
        valid = validate_document(customer_doc)
        if not valid:
            show_messagebox(pos_id, "$INVALID_CPF_CNPJ")

    fill_additional_info(pos_ot, "CPF", customer_doc)
    return customer_doc


def validate_document(customer_doc):
    valid = False
    if len(customer_doc) <= 11:
        valid = validar_cpf(customer_doc)
    elif len(customer_doc) > 11:
        valid = validar_cnpj(customer_doc)
    return valid


def fill_additional_info(pos_ot, properties, value):
    if pos_ot.additionalInfo:
        pos_ot.additionalInfo += "|"
    else:
        pos_ot.additionalInfo = ""
    pos_ot.additionalInfo += "{0}={1}".format(properties, value)


def validar_cpf(cpf):
    cpf = ''.join(re.findall('\d', str(cpf)))

    if (not cpf) or (len(cpf) < 11):
        return False

    inteiros = map(int, cpf)
    novo = inteiros[:9]

    while len(novo) < 11:
        r = sum([(len(novo) + 1 - i) * v for i, v in enumerate(novo)]) % 11

        if r > 1:
            f = 11 - r
        else:
            f = 0
        novo.append(f)

    if novo == inteiros:
        return cpf

    return False


def validar_cnpj(cnpj):
    cnpj = ''.join(re.findall('\d', str(cnpj)))

    if (not cnpj) or (len(cnpj) < 14):
        return False

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

    if novo == inteiros:
        return cnpj

    return False


def json_serialize(dictionary):
    # type: (Dict) -> str
    try:
        return json.dumps(dictionary, default=lambda o: getattr(o, '__dict__', str(o)))
    except ValueError as _:
        return dictionary
    
    
def compare_objects(obj1, obj2):
    return object_to_json(obj1) == object_to_json(obj2)


def object_to_json(obj):
    return json.dumps(obj, sort_keys=True, default=lambda o: getattr(o, '__dict__', str(o)))
