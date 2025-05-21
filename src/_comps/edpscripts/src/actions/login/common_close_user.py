# -*- coding: utf-8 -*-
import sysactions

from application.repository import AccountRepository

from actions.util import get_operator_info
from ..functions.do_transfer import do_transfer, get_justication
from .. import logger, SIGNED_IN_USER, mb_context
from .utils import close_user

USECS_PER_SEC = 1000000


def common_close_user(pos_id, model, user_id, auth_data=None):
    from msgbusboundary import MsgBusTableService as tableService

    _, _, session = get_operator_info(model, user_id)
    pod_function = sysactions.get_posfunction(model)
    is_quick_service = model.find("WorkingMode").get("usrCtrlType") != "TS"
    need_ask_justification = False
    if pod_function != "OT":
        done_transfer, need_ask_justification = do_transfer(pos_id, 6, user_id, is_quick_service)
        if not done_transfer:
            return False

    period = sysactions.get_business_period(model)
    pos_list = [pos_id] if is_quick_service else tableService().get_exclusive_pos_list(user_control_type="TS")
    pos_list = '|'.join(str(i) for i in pos_list)
    authorizer = auth_data[0] if auth_data else None

    logger.debug("Logoff POS %d - Deslogando operador %s" % (int(pos_id), user_id))
    if close_user(pos_id, user_id):
        logger.debug("Logoff POS %d - Operador %s deslogado com sucesso" % (int(pos_id), user_id))
        pos_ot = sysactions.get_posot(model)
        pos_ot.resetCurrentOrder(pos_id)

        sysactions.set_custom(pos_id, "VOIDAUTH_SESSION_DISABLED", "false", persist=True)
        sysactions.clear_custom(pos_id, SIGNED_IN_USER)
    else:
        logger.error("Logoff POS %d - Falha ao deslogar operador %s" % (int(pos_id), user_id))
        sysactions.show_messagebox(pos_id, "$OPERATION_FAILED", "$ERROR")
        return False

    sysactions.print_report(pos_id, model, True, "close_operator_report", pos_id, period, user_id, pos_list, session,
                            authorizer)

    if pod_function != "OT" and need_ask_justification:
        account_repository = AccountRepository(mb_context)
        get_justication(account_repository, pos_id, session)

    if need_ask_justification:
        sysactions.print_report(pos_id, model, True, "close_operator_report", pos_id, period, user_id, pos_list, session, authorizer)

    return True
