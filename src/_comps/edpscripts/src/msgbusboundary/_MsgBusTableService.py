from xml.etree import cElementTree as eTree

from application.domain import TableService, Table, TablePictureToOrdersParser
from pos_model import TableStatus
from sysactions import get_model, get_posot, get_poslist
from tablemgrapi import get_posts


class MsgBusTableService(TableService):
    def get_selected_table(self, pos_id, tables=None):
        if tables is None:
            tables = self.list_tables(pos_id)
        selected_tables = filter(lambda x: x.current_pos_id == pos_id, tables)
        return selected_tables[0] if len(selected_tables) > 0 else None

    def get_table(self, pos_id, table_id):
        tables = self.list_tables(pos_id)
        selected_table = filter(lambda x: x.id == table_id, tables)
        return selected_table[0] if len(selected_table) > 0 else None

    def list_tables(self, pos_id):
        pos_ts = _a_get_posts(pos_id)

        tables_list = []
        for table in pos_ts.listTables(withprops=1):
            table_obj = Table()
            table_obj.id = table["id"]
            table_obj.current_pos_id = table["currentPOSId"]
            table_obj.status = int(table["status"])
            table_obj.tab_id = table["properties"]["TAB_ID"] if table["typeDescr"] == 'Tab' and table["properties"] else None
            table_obj.business_period = int(table["businessPeriod"].replace("-", "")) if table["businessPeriod"] else None
            tables_list.append(table_obj)

        return tables_list

    def set_current_order(self, pos_id, order_id):
        model = get_model(pos_id)
        pos_ts = get_posts(model)
        table_id = self.get_selected_table(pos_id).id
        user_id = model.find("Operator").get("id")
        pos_ts.setCurrentOrder(user_id, table_id, order_id)

    def void_service_order(self, pos_id, table_id, order_id):
        model = get_model(pos_id)
        user_id = model.find("Operator").get("id")
        pos_ts = get_posts(model)
        pos_ts.voidServiceOrder(user_id, table_id, order_id)

    def start_service(self, pos_id, table_id="", seats="", tab_id=""):
        model = get_model(pos_id)
        pos_ts = get_posts(model)

        self.tab_id_is_valid(pos_id, tab_id, pos_ts)

        business_period = model.find("PosState").get("period")
        business_period = business_period[0:4] + "-" + business_period[4:6] + "-" + business_period[6:8]
        user_id = model.find("Operator").get("id")

        response = pos_ts.startService(user_id, business_period, table_id, seats, customprops={"TAB_ID": tab_id})

        if table_id == "":
            table_id = response["tableId"]

        return pos_ts.getTablePicture(table_id)

    def tab_id_is_valid(self, pos_id, tab_id, pos_ts=None):
        if not pos_ts:
            pos_ts = get_posts(get_model(pos_id))

        if tab_id != '':
            for table in pos_ts.listTables(withprops=1):
                if str(table["id"]).startswith("TAB") \
                        and int(table['status']) != TableStatus.CLOSED.value \
                        and table["properties"] is not None \
                        and "TAB_ID" in table["properties"] \
                        and int(table["properties"]["TAB_ID"]) == tab_id:
                    raise Exception("TAB_ALREADY_EXISTS")

    def is_a_tab(self, pos_id, table_id, table_picture=None):
        if not table_picture:
            table_picture = eTree.XML(self.get_table_picture(pos_id, table_id))

        if type(table_picture) in [str, unicode]:
            table_picture = eTree.XML(table_picture)

        if table_picture.get("id").startswith("TAB"):
            return True
        return False

    def recall_service(self, pos_id, table_id):
        model = get_model(pos_id)
        pos_ts = get_posts(model)
        user_id = model.find("Operator").get("id")

        return pos_ts.recallService(user_id, table_id)

    def store_service(self, pos_id, table_id):
        model = get_model(pos_id)
        pos_ts = get_posts(model)
        user_id = model.find("Operator").get("id")

        return pos_ts.storeService(user_id, table_id)

    def create_order(self, pos_id, table_id, pricelist=''):
        model = get_model(pos_id)
        pos_ts = get_posts(model)
        user_id = model.find("Operator").get("id")

        return pos_ts.createOrder(user_id, table_id, pricelist)

    def slice_service(self, pos_id, new_setup, src_table_id):
        model = get_model(pos_id)
        pos_ts = get_posts(model)
        user_id = model.find("Operator").get("id")

        return pos_ts.sliceService(user_id, new_setup, src_table_id)

    def get_table_picture(self, pos_id, table_id):
        pos_ts = _a_get_posts(pos_id)
        return pos_ts.getTablePicture(table_id)

    def get_current_pos_id(self, pos_id, table_id):
        model = get_model(pos_id)
        table = model.find('STORE_MODIFIED/Tables/Table[@id="{}"]'.format(table_id))
        return table.get("currentPOSId")

    def do_total_table(self, pos_id, table_id, tip_rate="", seat_distribution=None):
        model = get_model(pos_id)
        user_id = model.find("Operator").get("id")

        pos_ts = get_posts(model)
        return pos_ts.totalService(user_id, table_id, tip_rate, '', seat_distribution)

    def reopen_table(self, pos_id, table_id):
        model = get_model(pos_id)
        user_id = model.find("Operator").get("id")
        pos_ts = get_posts(model)

        return pos_ts.reopenService(user_id, table_id)

    def close_table(self, pos_id, table_id):
        model = get_model(pos_id)
        pos_ts = get_posts(model)
        user_id = model.find("Operator").get("id")

        return pos_ts.closeService(user_id, table_id)

    def set_table_available(self, pos_id, table_id):
        model = get_model(pos_id)
        pos_ts = get_posts(model)
        user_id = model.find("Operator").get("id")

        pos_ts.tableReady4Service(user_id, table_id)

    def get_current_table_id(self, pos_id):
        try:
            model = get_model(pos_id)
            table = model.find('STORE_MODIFIED/Tables/Table[@currentPOSId="{}"]'.format(pos_id))
            return table.get("id")
        except Exception as _:
            return None

    def clear_service_tenders(self, pos_id, table_id):
        model = get_model(pos_id)
        pos_ts = get_posts(model)
        user_id = model.find("Operator").get("id")

        return pos_ts.clearServiceTenders(user_id, table_id)

    def change_service_tip(self, pos_id, table_id, percentage=None, amount=None):
        model = get_model(pos_id)
        pos_ts = get_posts(model)
        user_id = model.find("Operator").get("id")

        return pos_ts.changeServiceTip(user_id, table_id, percentage, amount)

    def set_table_custom_property(self, pos_id, property, propvalue=None, tableid=None, serviceid=None):
        model = get_model(pos_id)
        pos_ts = get_posts(model)
        pos_ts.setCustomProperty(property, propvalue, tableid, serviceid)

    def get_table_custom_property(self, pos_id, property, tableid=None, serviceid=None):
        model = get_model(pos_id)
        pos_ts = get_posts(model)
        return pos_ts.getCustomProperty(property, tableid, serviceid)

    def register_service_tender(self, pos_id, table_id, tender_id, amount, orders=None, tender_details=""):
        model = get_model(pos_id)
        pos_ts = get_posts(model)
        user_id = model.find("Operator").get("id")

        return pos_ts.registerServiceTender(
            user_id,
            table_id,
            tender_id,
            str(amount),
            tenderdetail=tender_details,
            orders=orders)

    def get_table_orders(self, pos_id, table_id, table_picture=None):
        if table_picture is None:
            table_picture = self.get_table_picture(pos_id, table_id)
        orders = TablePictureToOrdersParser.parse(table_picture)

        return orders

    def get_service_seats_count(self, pos_id):
        table_id = self.get_current_table_id(pos_id)
        table_picture = self.get_table_picture(pos_id, table_id)
        table_picture_xml = eTree.XML(table_picture)
        service_seats = int(table_picture_xml.get("serviceSeats"))
        return int(service_seats)

    def set_sale_line_seat(self, pos_id, seat_number, line_number, item_id, level, part_code):
        self._set_order_custom_property(pos_id, 'seat', seat_number, line_number, item_id, level, part_code)

    @staticmethod
    def get_exclusive_pos_list(user_control_type=None, pos_list=None):
        if not pos_list:
            pos_list = get_poslist()

        pos_list = list(pos_list)

        if not user_control_type:
            return sorted(pos_list)

        for pos_id in sorted(pos_list):
            model = get_model(pos_id)
            working_mode = model.find('.//WorkingMode').get('usrCtrlType')
            if working_mode != user_control_type:
                pos_list.remove(pos_id)
        return sorted(pos_list)

    def _set_order_custom_property(self, pos_id, key, value, *params):
        model = get_model(pos_id)
        pos_ot = get_posot(model)
        pos_ot.setOrderCustomProperty(key, value, '', *params)


def _a_get_posts(pos_id):
    model = get_model(pos_id)
    return get_posts(model)
