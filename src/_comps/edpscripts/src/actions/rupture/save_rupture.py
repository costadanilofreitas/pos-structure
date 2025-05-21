# -*- coding: utf-8 -*-
import json

import sysactions
from bustoken import TK_RUPTURA_UPDATE_ITEMS
from msgbus import TK_SYS_NAK, FM_PARAM


from .. import logger
from .. import mb_context
from ..products import getProducts


@sysactions.action
def save_rupture(pos_id, enabled_ingredients, disabled_ingredients):
    model = sysactions.get_model(pos_id)

    try:
        rupture_status_json = json.dumps({
            'enabled': json.loads(enabled_ingredients),
            'disabled': json.loads(disabled_ingredients)})

        user_id = '{} / {}'.format(sysactions.get_custom(model, 'Last Manager ID'),
                                   sysactions.get_operator_session(model))

        # save rupture data using ruptura component
        msg = mb_context.MB_EasySendMessage(
                "Ruptura",
                TK_RUPTURA_UPDATE_ITEMS,
                FM_PARAM,
                '\0'.join(map(str, [rupture_status_json, user_id, pos_id]))
            )

        if msg.token == TK_SYS_NAK:
            raise Exception(msg.data)

        return

    except BaseException as e:
        logger.exception('[save_rupture] Exception {}'.format(e))
        sysactions.show_messagebox(pos_id, "Erro ao salvar os dados", "$INFORMATION", buttons="Sair")
        return
