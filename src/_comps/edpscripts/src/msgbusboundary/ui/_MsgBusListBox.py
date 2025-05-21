from application.domain.ui import ListBox
from sysactions import show_listbox


class MsgBusListBox(ListBox):
    def show_listbox(self, pos_id, options, message='$SELECT_AN_OPTION', title='', def_value='', buttons='$OK|$CANCEL',
                     icon='', timeout=60000, asynch=False):
        selected = show_listbox(pos_id, options, "$SELECT_SEAT_FOR_LINE", "$SEAT_SELECTION_TITLE", def_value, buttons,
                                icon, timeout, asynch)
        return selected
