from application.domain.ui import MessageBox
from sysactions import show_messagebox


class MsgBusMessageBox(MessageBox):

    def show(self, pos_id, message, title='$INFORMATION', icon='info', buttons='$OK', timeout=60000, asynch=False, linefeed='\\', focus=True):
        show_messagebox(
            pos_id,
            message,
            title,
            icon,
            buttons,
            timeout,
            asynch,
            linefeed,
            focus
        )
