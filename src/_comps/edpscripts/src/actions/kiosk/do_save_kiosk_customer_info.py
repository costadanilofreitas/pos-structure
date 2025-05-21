# -*- coding: utf-8 -*-

import json

import sysactions
from old_helper import validar_cpf


@sysactions.action
def do_save_kiosk_customer_info(pos_id, name, cpf=''):
    model = sysactions.get_model(pos_id)

    sysactions.check_current_order(pos_id, model=model, need_order=True)

    errors = []

    pos_ot = sysactions.get_posot(model)

    if cpf and not validar_cpf(cpf):
        errors.append(['doc', '$INVALID_CPF_ERROR'])

    if errors:
        return json.dumps(errors)

    if cpf:
        pos_ot.setOrderCustomProperty('CUSTOMER_DOC', cpf)
