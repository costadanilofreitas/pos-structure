# -*- coding: utf-8 -*-
# Python module responsible to handle POS actions
# All actions are broad-casted by the PosController using a "POS_ACTION" event subject
#
# Copyright (C) 2008-2012 MWneo Corporation
#
# $Id$
# $Revision$
# $Date$
# $Author$

import re
from sysactions import get_cfg, get_model, get_used_service, show_confirmation, show_info_message, show_messagebox, read_msr, \
    close_asynch_dialog, show_keyboard, authenticate_user, sys_log_info, AuthenticationFailed, set_custom, get_custom

__all__ = ['get_authorization', 'validar_cpf', 'validar_cnpj']


def get_authorization(posid, min_level=None, model=None, timeout=60000, is_login=True):
    """ get_authorization(posid, min_level=None, model=None, timeout=60000) -> True or False
    Requests authorization for an operation.
    The "authorizationType" parameter on PosController defines how the authorization will be requested.
    Possible values are: ("login", "card")
    @param posid - POS id
    @param min_level - optional minimum user level required for this operation
    @param model - optional POS model (will be retrieved if necessary)
    @param timeout - operation timeout (in millis)
    @return True if authorization succeeded, False otherwise
    """

    auth_type = get_cfg(posid).key_value("authorizationType", "card").lower()

    #
    # CARD authorization
    #
    if auth_type == "card":
        # Check wich card reader (MSR) we should use
        model = model or get_model(posid)
        msr_name = get_used_service(model, "msr")

        if not msr_name:
            # No card reader configured - on DEMO mode we can just show a confirmation
            demo_mode = (get_cfg(posid).key_value("demoMode", "false").lower() == "true")
            if demo_mode:
                return show_confirmation(posid, message="$CONFIRM_DEMO_MODE")

            show_info_message(posid, "$CARDREADER_NOT_CONFIGURED", msgtype="error")

            return False

        dlgid = show_messagebox(posid, "$SWIPE_CARD_TO_AUTHORIZE", "$MAGNETIC_STRIPE_READER", "swipecard", "$CANCEL", timeout, True)
        tracks = None

        try:
            # Read tracks from the card reader
            tracks = read_msr(msr_name, timeout, dlgid)
        finally:
            close_asynch_dialog(posid, dlgid)

        if tracks:
            # TODO: parse tracks and validate level if necessary
            return True

        return False

    #
    # LOGIN authorization
    #
    if auth_type == "login":
        # Request user ID and password to GUI
        userid = show_keyboard(posid, "$AUTH_ENTER_USER_ID", title="", mask="INTEGER", numpad=True)
        if userid is None:
            return  # User cancelled, or timeout

        passwd = show_keyboard(posid, message="$ENTER_PASSWORD|%s" % (userid), title="$OPERATOR_LOGIN" if is_login else "", is_password=True, numpad=True)
        if passwd is None:
            return  # User cancelled, or timeout

        # Verify the user id/password/level
        try:
            user = authenticate_user(userid, passwd, min_level=min_level)
            level = user.get('Level', None)
            set_custom(posid, 'Authorization Level', level, False)
            set_custom(posid, 'Last Manager ID', userid, False)
            # Success
            sys_log_info("Authentication succeeded for POS id: %s, user id: %s" % (posid, userid))
            return True
        except AuthenticationFailed:
            show_info_message(posid, "Autenticação não autorizada !!!", msgtype="error")

        return False

    return False


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
