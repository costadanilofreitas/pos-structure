from sysactions import show_messagebox, show_listbox, get_model, print_report, action, show_keyboard, StopAction

from application.repository import AccountRepository
from actions.util import get_operator_info
from manager.reports import get_report_date

from .. import mb_context


@action
def show_operator_closing(pos_id, operator_id):
    end_date, operator_id, start_date = get_manual_inserted_data(operator_id, pos_id)

    model = get_model(pos_id)
    _, _, session = get_operator_info(model, operator_id)

    options, sessions = get_date_options_and_sessions(end_date, operator_id, pos_id, session, start_date)

    selected_date = show_listbox(pos_id, options, message="$SELECT_A_DATE")
    if selected_date is None:
        raise StopAction()

    session = sessions[selected_date]
    selected_date = session.split("period=")[1]

    print_report(pos_id,
                 model,
                 True,
                 "close_operator_report",
                 pos_id,
                 selected_date,
                 operator_id,
                 None,
                 session,
                 None)


def get_manual_inserted_data(operator_id, pos_id):
    start_date = get_report_date(pos_id, "$TYPE_INITIAL_DATE")
    if start_date is None:
        raise StopAction()

    end_date = get_report_date(pos_id, "$TYPE_FINAL_DATE")
    if end_date is None:
        raise StopAction()

    if not operator_id:
        operator_id = show_keyboard(pos_id, "$TYPE_OPERATOR_ID_MESSAGE", mask="INTEGER", numpad=True)
        if operator_id is None:
            raise StopAction()

    return end_date, operator_id, start_date


def get_date_options_and_sessions(end_date, operator_id, pos_id, session, start_date):
    account_repository = AccountRepository(mb_context)
    sessions = account_repository.get_closing_operator_sessions(pos_id, operator_id, start_date, end_date)

    if session in sessions:
        sessions.remove(session)

    if not sessions:
        show_messagebox(pos_id, "$THERE_ARE_NO_DATA_TO_SHOW", "$INFORMATION")
        raise StopAction()

    options = []
    for current_session in sessions:
        session = current_session.split("period=")[1].split(",")[0]
        counter = current_session.split("count=")[1].split(",")[0]
        formatted_option = session[6:] + "/" + session[4:6] + "/" + session[:4] + " (" + counter + ")"
        options.append(formatted_option)

    return options, sessions
