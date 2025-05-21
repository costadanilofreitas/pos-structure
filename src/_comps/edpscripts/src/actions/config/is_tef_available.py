from bustoken import TK_SITEF_AVAILABLE
from sysactions import action

from .. import mb_context


@action
def is_tef_available(pos_id):
    try:
        mb_context.MB_EasySendMessage("Sitef%02d" % int(pos_id), token=TK_SITEF_AVAILABLE)
        return "true"
    except:
        return "false"
