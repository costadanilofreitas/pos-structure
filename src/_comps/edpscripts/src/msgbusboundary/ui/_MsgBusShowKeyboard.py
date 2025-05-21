from application.domain.ui import ShowKeyboard
from sysactions import show_keyboard, is_valid_date, show_info_message


class MsgBusShowKeyboard(ShowKeyboard):

    def show(self, pos_id, message, title='$INPUT_DATA', buttons='$OK|$CANCEL',
             icon='info', timeout=60000, mask='', is_password=False, def_value='', min_value='', maxvalue='',
             num_pad=False, no_pad=False, no_input=False, asynch=False):
        return show_keyboard(pos_id, message, title, info_text, buttons, icon, timeout, mask, is_password, def_value,
                             min_value, maxvalue, num_pad, no_pad, no_input, asynch)

    def show_date(self, pos_id, message, title="", show_message_wrong_input_date=False):
        date = show_keyboard(pos_id, message, title="", mask="DATE", numpad=True)

        if date is None:
            return None
        if not is_valid_date(date):
            show_info_message(pos_id, "$INVALID_DATE", msgtype="error")
            return None

        return date
