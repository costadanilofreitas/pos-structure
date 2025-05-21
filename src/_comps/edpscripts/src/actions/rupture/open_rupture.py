import json

import sysactions

import get_products
from .. import logger


@sysactions.action
def open_rupture(pos_id):
    try:
        enabled_ingredients = get_products.get_enabled_products()
        disabled_ingredients = get_products.get_disabled_products()

    except BaseException as e:
        logger.exception('[rupture_items] Exception {}'.format(e))
        sysactions.show_messagebox(pos_id, "Erro ao obter os dados", "$INFORMATION", buttons="Sair")
        return

    dialog_contents = {
        "enabledIngredients": enabled_ingredients,
        "disabledIngredients": disabled_ingredients
    }

    sysactions.show_any_dialog(pos_id, "rupture", "", "", json.dumps(dialog_contents), "", "", 6000000, "", "", "", "",
                               "", False)
