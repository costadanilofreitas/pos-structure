import sysactions

from .. import logger

from .. import mb_context


@sysactions.action
def open_delivery_store(pos_id, store_id):
    try:
        mb_context.MB_EasyEvtSend("OpenDeliveryStore", type="", xml=store_id, sourceid=int(pos_id))

    except Exception as e:
        sysactions.show_messagebox(pos_id, "$ERROR_OPENING_DELIVERY_STORE")
        logger.error(e)
        return False

    return True
