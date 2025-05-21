# -*- coding: utf-8 -*-

import io
import json
import logging
import collections

from threading import Thread, Condition, Lock
from time import sleep
from xml.etree import cElementTree as eTree
from datetime import datetime, timedelta

import requests
import sysactions
from msgbus import TK_SYS_NAK, TK_SYS_ACK, FM_PARAM, TK_POS_GETPOSLIST, TK_POS_LISTUSERS
from sysactions import send_message, set_custom, get_user_information

from Model import StoreGoals, Goals, ItemGoals, OperatorGoals, StoreGoalsCache, ItemGoalsCache, GoalsCache

DATE_FORMAT = "%Y-%m-%d"

try:
    to_unicode = unicode
except NameError:
    to_unicode = str

logger = logging.getLogger("DailyGoals")


class DailyGoalsProcessor(Thread):
    def __init__(self, mb_context, service_url, api_user, api_password, goals_cache_file_name):
        super(DailyGoalsProcessor, self).__init__()
        logger.info('[DailyGoalsProcessor __init__] Begin')
        self.mb_context = mb_context
        sysactions.mbcontext = mb_context
        self.thread_condition = Condition()
        self.service_url = service_url
        self.api_user = api_user
        self.api_password = api_password
        self.goals_cache_file_name = goals_cache_file_name
        self.daily_goals_cache = []
        self.today_goals = None
        self.daily_goals = None
        self.timestamp = None
        self.debug_metas = False
        self.total_sold = 0.0
        self.lock = Lock()

        self.pos_list = None
        self.bk_number = None

    def configure(self, bk_number):
        logger.info('[configure] Begin')
        self.bk_number = bk_number

        try:
            self._get_pos_list()
            response = self.update_daily_goals()
            if response[0] == TK_SYS_ACK:
                self.update_daily_sold(get_values_from_database=True)
            else:
                for pos_id in self.pos_list:
                    set_custom(pos_id, 'DAILY_GOALS', '{}')

        except Exception as _:
            logger.exception('[configure] Exception:')

        logger.info('[configure] End')

    def _get_pos_list(self):
        retry_cnt = 10
        while retry_cnt:
            msg = self.mb_context.MB_EasySendMessage("PosController", TK_POS_GETPOSLIST)
            if msg.token == TK_SYS_NAK:
                retry_cnt -= 1
                sleep(1)
            else:
                self.pos_list = sorted(map(int, msg.data.split("\0")))
                retry_cnt = 0

    def update_daily_goals(self):
        logger.info('[update_daily_goals] Begin')
        now = datetime.now()
        cur_date = now.strftime("%d/%m/%Y")
        final_date = (now + timedelta(days=5)).strftime("%d/%m/%Y")

        self.timestamp = cur_date
        self.update_daily_goals_cache_from_bk_office(cur_date, final_date)

        try:
            items_goals, store_goals = self._load_goals_from_cache()
            if not store_goals and not items_goals:
                return TK_SYS_NAK, 'NAK'

            item_goals = self._populate_item_goals(items_goals)
            store_goals = self._populate_store_goals(store_goals, item_goals)

            with self.lock:
                self.today_goals = GoalsCache(store_goals, item_goals)
            logger.info('[update_daily_goals] End')
            return TK_SYS_ACK, 'OK'

        except Exception as _:
            logger.exception('[update_daily_goals] Exception. Sort issue')
            return TK_SYS_NAK, 'NAK'

    def update_daily_goals_cache_from_bk_office(self, cur_date, final_date):
        try:
            response = self._load_daily_goals_from_bk_office(cur_date, final_date)
            if response.status_code == requests.codes.ok:
                response_json = json.loads(response.text)

                res_status = response_json.get('status')
                logger.info("[update_daily_goals] Response from BKOffice: {}".format(res_status))
                if res_status is not None:
                    req_status = res_status.get('status', False)
                    req_perm = res_status.get('permission', False)
                    if req_status and req_perm:
                        logger.info("[update_daily_goals] Daily goals taken from API")
                        res_result_metas_product = response_json.get('list', [])
                        res_result_metas_total = response_json.get('totalDays', {})

                        store_goals = self._parse_bk_office_store_goals(res_result_metas_total)
                        items_goals = self._parse_bk_office_items_goals(res_result_metas_product)
                        goals = GoalsCache(store_goals, items_goals)

                        with io.open(self.goals_cache_file_name, 'w', encoding='utf8') as outfile:
                            json_goals = json.dumps(goals, default=lambda o: o.__dict__, sort_keys=True)
                            outfile.write(to_unicode(json_goals))
                    else:
                        raise Exception("Request Metas failed, take them from cache")
            else:
                logger.info("Response com error code: {}".format(response.status_code))
                raise Exception("Request Metas failed, take them from cache")

        except Exception as _:
            logger.exception(
                '[update_daily_goals] Exception. Request error for service_url: {}'.format(self.service_url))

    @staticmethod
    def _populate_store_goals(store_goals_json, item_goals):
        store_goals = None
        if store_goals_json:
            for item in store_goals_json:
                start_date = datetime.strptime(item["startDate"], DATE_FORMAT)
                end_date = datetime.strptime(item["endDate"], DATE_FORMAT) + timedelta(days=1)
                if start_date < datetime.now() < end_date:
                    total_sales = item.get('totalSales')
                    average_sale_value = item.get('averageSaleValue')
                    operator_sale_goal = item.get('operatorSaleValue')
                    store_goals = StoreGoals(total_sales, average_sale_value, operator_sale_goal, item_goals)
                    break
        return store_goals

    @staticmethod
    def _populate_item_goals(items_goals_json):
        item_goals = []
        if items_goals_json:
            for item in items_goals_json:
                start_date = datetime.strptime(item["startDate"], DATE_FORMAT)
                end_date = datetime.strptime(item["endDate"], DATE_FORMAT) + timedelta(days=1)
                if start_date < datetime.now() < end_date:
                    name = item.get('name')
                    part_codes = item.get('partCodes')
                    quantity = item.get('quantity')
                    quantity_operator_goal = item.get('operatorQuantity')
                    item_goals.append(ItemGoals(name, part_codes, quantity, quantity_operator_goal, 0))
        return item_goals

    def _load_goals_from_cache(self):
        with open(self.goals_cache_file_name) as data_file:
            logger.info('[update_daily_goals] Taking goals from cache file')
            response_json = json.load(data_file)
            store_goals_json = response_json.get('storeGoals', [])
            items_goals_json = response_json.get('itemGoals', {})
        return items_goals_json, store_goals_json

    def _load_daily_goals_from_bk_office(self, cur_date, final_date):
        params = {
            "bkNumber": self.bk_number,
            "initialDate": cur_date,
            "finalDate": final_date,
        }
        headers = {'Content-type': 'application/json'}
        response = requests.post(
            self.service_url,
            headers=headers,
            data=json.dumps(params),
            auth=requests.auth.HTTPBasicAuth(self.api_user, self.api_password),
            timeout=15.0
        )
        return response

    @staticmethod
    def _parse_bk_office_store_goals(bk_office_store_goals):
        store_goals = []
        values_dict = {}
        for key, value in bk_office_store_goals.items():
            item_date = datetime.strptime(key[5:], '%d/%m/%Y')
            values_dict[item_date] = value

        values_dict = collections.OrderedDict(sorted(values_dict.items()))

        last_store_goal = None
        for key, value in values_dict.items():
            string_date = key.strftime(DATE_FORMAT)
            store_goal = StoreGoalsCache(string_date, string_date, value, 0)

            if last_store_goal is not None and \
                    datetime.strptime(last_store_goal.end_date, DATE_FORMAT) + timedelta(days=1) == key and \
                    last_store_goal.total_sales == value:
                store_goals[-1].end_date = string_date
            else:
                store_goals.append(store_goal)

            last_store_goal = store_goal

        return store_goals

    @staticmethod
    def _parse_bk_office_items_goals(bk_office_items_goals):
        items_goals = []
        categories_dict = {}
        for item in bk_office_items_goals:
            name = item["alavanca"]
            item_date = item["referenceDate"]

            if name + "_" + item_date in categories_dict:
                categories_dict[name + "_" + item_date].append(item)
            else:
                categories_dict[name + "_" + item_date] = [item]

        for category, items in categories_dict.items():
            item_goal_cache = None
            for item in items:
                name = item["alavanca"]
                item_date = datetime.strptime(item["referenceDate"], '%d/%m/%Y')
                quantity = int(item["targetQuantity"])
                part_code = item["sku"]["skuId"]

                if item_goal_cache is None:
                    temp_date = item_date.strftime(DATE_FORMAT)
                    item_goal_cache = ItemGoalsCache(temp_date, temp_date, name, [part_code], quantity, 0)
                else:
                    item_goal_cache.quantity += quantity
                    item_goal_cache.part_codes.append(part_code)

            items_goals.append(item_goal_cache)

        return items_goals

    def _update_total_sold_from_mem(self, xml_order, number_of_seats):
        operator_id = xml_order.get("sessionId").split("user=")[1].split(",")[0]
        daily_goals = self.daily_goals
        if daily_goals is None:
            return

        if not any(x.id == operator_id for x in daily_goals.operator_goals):
            self._add_new_operator_to_mem(daily_goals, operator_id)

        added_tickets = False
        sale_lines = xml_order.findall("SaleLine")
        for line in sale_lines:
            part_code = line.get("partCode")
            for operator_daily_goal in daily_goals.operator_goals:
                if operator_daily_goal.id == operator_id:
                    for daily_goal_item in operator_daily_goal.item_goals:
                        if part_code in daily_goal_item.part_codes:
                            for item_goal in operator_daily_goal.item_goals:
                                if part_code in item_goal.part_codes:
                                    item_goal.quantity_sold += float(line.get("qty"))

                            for item_goal in daily_goals.store_goals.item_goals:
                                if part_code in item_goal.part_codes:
                                    item_goal.quantity_sold += float(line.get("qty"))
                    if line.get("unitPrice") is not None:
                        operator_daily_goal.amount_sold += float(line.get("qty")) * float(line.get("unitPrice"))
                        daily_goals.store_goals.sold_quantity += float(line.get("qty")) * float(line.get("unitPrice"))

                    if not added_tickets:
                        operator_daily_goal.tickets += number_of_seats
                        added_tickets = True

        return daily_goals

    def _add_new_operator_to_mem(self, daily_goals, operator_id):
        store_goals = self.today_goals.store_goals
        items_goals = self.today_goals.item_goals
        operator_item_goals = []
        for item_goal in items_goals:
            operator_item_goals.append(ItemGoals(item_goal.name,
                                                 item_goal.part_codes,
                                                 item_goal.quantity_goal,
                                                 item_goal.quantity_operator_goal,
                                                 0))
        operator_goals = OperatorGoals(operator_id,
                                       store_goals.operator_sale_goal,
                                       0,
                                       store_goals.average_sale_goal,
                                       operator_item_goals,
                                       0)
        daily_goals.operator_goals.append(operator_goals)

    def _get_current_sold_qty_items_from_database(self, items, initial_date, end_date, operator_id):
        logger.info('[_get_current_sold_qty_items_from_database] Begin')

        total_sold = 0
        pmix_order_items = json.loads(sysactions.generate_report("pmix_order_items",
                                                                 initial_date,
                                                                 end_date,
                                                                 self.bk_number,
                                                                 operator_id))

        for pmix_item in pmix_order_items:
            for item in items:
                for part_code in item.part_codes:
                    if int(part_code) == pmix_item['pcode']:
                        item.quantity_sold += pmix_item['quantity']
            total_sold += pmix_item['quantity'] * float(pmix_item["unit_price"])

        logger.info('[_get_current_sold_qty_items_from_database] End')

        return total_sold

    def update_daily_sold(self, order_pict='', operator_id="", number_of_seats=1, get_values_from_database=False):
        if not self.today_goals:
            return TK_SYS_NAK, 'NAK'

        try:
            now = datetime.now()
            cur_date = now.strftime("%d/%m/%Y")
            if self.timestamp != cur_date:
                self.update_daily_goals()
                get_values_from_database = True

            if self.daily_goals is None:
                get_values_from_database = True

            with self.lock:
                if order_pict:
                    self.daily_goals = self._update_total_sold_from_mem(order_pict, number_of_seats)
                elif get_values_from_database:
                    store_goals = self.today_goals.store_goals
                    items_goals = self.today_goals.item_goals
                    operators_goals = []

                    initial_date = datetime.now()
                    end_date = datetime.now()
                    self._populate_operators_sold_values(end_date,
                                                         initial_date,
                                                         store_goals,
                                                         items_goals,
                                                         operators_goals)
                    if store_goals is not None:
                        self._populate_store_sold_values(end_date, initial_date, operator_id, store_goals)
                    self.daily_goals = Goals(store_goals, operators_goals)

                goals_str = json.dumps(self.daily_goals, default=lambda o: o.__dict__, sort_keys=True)
                logger.info(goals_str)
            for pos_id in self.pos_list:
                set_custom(pos_id, 'DAILY_GOALS', goals_str)
        except Exception as _:
            logger.exception('[update_daily_sold] Exception:')
            return TK_SYS_NAK, 'NAK'

        return TK_SYS_ACK, 'OK'

    def _populate_store_sold_values(self, end_date, initial_date, operator_id, store_goals):
        store_goals.sold_quantity = self._get_current_sold_qty_items_from_database(store_goals.item_goals,
                                                                                   initial_date,
                                                                                   end_date,
                                                                                   operator_id)

    def _populate_operators_sold_values(self, end_date, initial_date, store_goals, item_goals, operators_goals):
        users_tickets = sysactions.generate_report("generate_tickets_report", initial_date)
        logger.info(users_tickets)
        users_tickets_json = json.loads(users_tickets)

        for op in self._get_all_opened_users():
            operator_item_goals = []
            for item_goal in item_goals:
                operator_item_goals.append(ItemGoals(item_goal.name,
                                                     item_goal.part_codes,
                                                     item_goal.quantity_goal,
                                                     item_goal.quantity_operator_goal,
                                                     0))

            user_tickets = list({int(v) for k, v in users_tickets_json.items() if k.startswith(op)})
            user_tickets = 0 if len(user_tickets) == 0 else user_tickets[0]

            operator_goals = OperatorGoals(op,
                                           store_goals.operator_sale_goal if store_goals is not None else 0,
                                           0,
                                           store_goals.average_sale_goal if store_goals is not None else 0,
                                           operator_item_goals,
                                           user_tickets)
            operator_goals.amount_sold = self._get_current_sold_qty_items_from_database(operator_goals.item_goals,
                                                                                        initial_date,
                                                                                        end_date,
                                                                                        op)
            operators_goals.append(operator_goals)

    @staticmethod
    def _get_all_opened_users():
        users_list = []

        for user in eTree.XML(get_user_information()).findall(".//user"):
            users_list.append(user.get("UserId"))

        return users_list

    @staticmethod
    def get_exclusive_pos_list(user_control_type=None, pos_list=None):
        if not pos_list:
            pos_list = sysactions.get_poslist()

        pos_list = sorted(list(pos_list))

        if not user_control_type:
            return pos_list

        for pos_id in pos_list:
            model = sysactions.get_model(pos_id)
            working_mode = model.find('.//WorkingMode').get('usrCtrlType')
            if working_mode != user_control_type:
                pos_list.remove(pos_id)
        return pos_list

    @staticmethod
    def _get_pos_users(pos_id):
        msg = send_message("POS%d" % int(pos_id), TK_POS_LISTUSERS, FM_PARAM, "%s" % pos_id)
        if msg.token == TK_SYS_NAK:
            raise Exception("Fail listing operators")
        xml = eTree.XML(msg.data)
        return [tag for tag in xml.findall("User")]
