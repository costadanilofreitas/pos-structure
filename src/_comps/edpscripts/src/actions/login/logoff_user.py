# -*- coding: utf-8 -*-
import sysactions

from common_close_user import common_close_user
from .. import logger
from ..models import UserLevels
from ..util import get_authorization


@sysactions.action
def logoffuser(pos_id, *args):
    logger.debug("Logoff POS %d - Iniciando logoff." % int(pos_id))

    model = sysactions.get_model(pos_id)
    sysactions.check_current_order(pos_id, model=model, need_order=False)

    operator = model.find("Operator")
    if operator is None:
        return False

    user_id = operator.get("id")
    response, auth_data = get_authorization(pos_id, min_level=UserLevels.MANAGER.value, model=model)
    if not response:
        return False

    return common_close_user(pos_id, model, user_id, auth_data)
