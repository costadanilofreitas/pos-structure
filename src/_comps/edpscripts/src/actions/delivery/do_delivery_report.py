import sysactions
from msgbus import TK_SYS_ACK
from bustoken import TK_REMOTE_ORDER_GET_POS_ID
from manager.reports import cashReport
from .. import mb_context


@sysactions.action
def do_delivery_report(pos_id):
    has_delivery = mb_context.MB_LocateService(mb_context.hv_service, 'RemoteOrder', maxretries=1)
    if has_delivery:
        msg = mb_context.MB_EasySendMessage('RemoteOrder', TK_REMOTE_ORDER_GET_POS_ID, data='', timeout=5000*1000)
        if msg.token == TK_SYS_ACK:
            remote_pos_id = msg.data
            cashReport(pos_id, ask_operator="notAsk", date_type="RealDate", ask_pos=int(remote_pos_id))
    return True

