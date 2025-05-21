# -*- coding: utf-8 -*-
import bustoken
from actions import mb_context
from sysactions import get_model, action, show_any_dialog
from systools import sys_log_error


@action
def show_daily_goals(pos_id, operator_id, show_amount_chart, show_items_chart, show_operators_table, show_average_ticket_chart):
    update_daily_goals(pos_id)

    return show_any_dialog(pos_id, "dailyGoals", "message", "title", "", "", "", 600000,
                           operator_id + "|" + show_amount_chart + "|" + show_items_chart + "|" +
                           show_operators_table + "|" + show_average_ticket_chart,
                           "", "", "", None, False)


def update_daily_goals(pos_id):
    try:
        model = get_model(pos_id)
        daily_goals = model.findall("Custom[@name='DAILY_GOALS']")
        if len(daily_goals) == 0:
            mb_context.MB_EasySendMessage("DailyGoals", bustoken.TK_DAILYGOALS_UPDATE_TOTAL_SOLD)
    except (Exception, BaseException) as _:
        sys_log_error("[update_daily_goals]")
