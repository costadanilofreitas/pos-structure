from application.domain import TableService  # noqa


class DoChangeTipInteractor(object):
    def __init__(self, table_service):
        # type: (TableService) -> None
        self.table_service = table_service

    def execute(self, pos_id, table_id, percentage, amount):
        # type: (str, str, str, str) -> str

        self.table_service.clear_service_tenders(pos_id, table_id)

        if (percentage != "" and percentage != "0") and (amount != "" and amount != "0"):
            raise Exception("Percentage and amount can not be passed in same time")
        elif percentage == "" and amount == "":
            raise Exception("Percentage or amount must be a valid value")

        if percentage != "":
            return self.table_service.change_service_tip(pos_id, table_id, percentage)
        if amount != "":
            return self.table_service.change_service_tip(pos_id, table_id, '', amount)
