from sysactions import send_message, check_operator_logged, get_model, action
from msgbus import MBException, TK_CDRAWER_OPEN


@action
def doOpenDrawer(pos_id, check_oper="true", *args):
    model = get_model(pos_id)
    if check_oper == "true":
        check_operator_logged(pos_id, model=model, can_be_blocked=False)

    drawers = model.findall("CashDrawer")
    for drawer in drawers:
        from threading import Thread
        Thread(target=thread_open_drawer, args=(drawer,)).start()


def thread_open_drawer(drawer):
    try:
        send_message(drawer.get("name"), TK_CDRAWER_OPEN)
    except MBException:
        pass
