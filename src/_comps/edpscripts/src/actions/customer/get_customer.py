from sysactions import action, show_messagebox, close_asynch_dialog

from .customer import Customer

dialog_id = None


@action
def get_customer(pos_id, phone):
    global dialog_id
    dialog_id = show_messagebox(pos_id, "$SEARCHING_CUSTOMER", buttons="", asynch=True)
    
    customer = Customer().get_customer(phone)
    return customer


@action
def get_customer_search_finished(pos_id, error="false"):
    close_asynch_dialog(pos_id, dialog_id)
    if error == "true":
        show_messagebox(pos_id, "$CUSTOMER_NOT_FOUND", buttons="OK")
