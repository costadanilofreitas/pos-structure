import json

from application.domain import TableService, I18n  # noqa
from application.domain.ui import ListBox
from sysactions import show_any_dialog


class ChooseLineSeatInteractor(object):
    def __init__(self, table_service, i18n, list_box):
        # type: (TableService, I18n, ListBox) -> None
        self.table_service = table_service
        self.i18n = i18n
        self.list_box = list_box

    def execute(self, pos_id, sale_line_json):
        seats_count = self.table_service.get_service_seats_count(pos_id)

        labels = self.i18n.internationalize(["$NO_SEAT", "$SEAT"])
        options = [labels["$NO_SEAT"]]

        for i in range(1, seats_count + 1):
            options.append(labels["$SEAT"].format(str(i)))

        selected = show_any_dialog(pos_id, "filteredListBox", "", "$SELECT_SEAT_FOR_LINE", "|".join(options), "", "",
                        600000, "NOFILTER", "", "", "", None, False)
        if selected is None:
            return

        selected = int(selected)
        seat = selected
        sale_line = json.loads(sale_line_json)

        self.table_service.set_sale_line_seat(pos_id, seat,
                                              sale_line["lineNumber"],
                                              sale_line["itemId"],
                                              sale_line["level"],
                                              sale_line["partCode"])
