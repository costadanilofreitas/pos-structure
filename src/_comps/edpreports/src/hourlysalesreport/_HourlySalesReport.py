# encoding: utf-8
import time
import datetime
import collections
from cStringIO import StringIO
import cfgtools
import os

import sysactions

from dateutil import tz
from utils import report_default_header, DATE_TIME_FMT, add_table_line, empty_line, center, double_line_separator, \
    single_line_separator, get_store_id
from model import IntervalConfiguration
from old_helper import convert_from_localtime_to_utc, convert_from_utf_to_localtime


class HourlySalesReport(object):
    def __init__(self, order_repository):
        self.order_repository = order_repository
        self.hourly_header = ["Tipo", "Hora", "Vendas", "TC", "TM"]
        self.hourly_columns_height = [10, 6, 9, 5, 8]
        self.houry_align = ['left', 'right', 'right', 'right', 'right']
        self.houry_format_type = ['string', 'string', 'float', 'integer', 'float']
        self.grouped_header = ["Tipo", "Vendas", "TC", "TM"]
        self.grouped_columns_height = [16, 9, 5, 8]
        self.grouped_align = ['left', 'right', 'right', 'right']
        self.grouped_format_type = ['string', 'float', 'integer', 'float']
        self.store_id = get_store_id()

    def generate_hourly_sales_report(self, pos_id, user_id, period):
        model = sysactions.get_model(pos_id)
        report = StringIO()
        title = "Relatorio de vendas por intervalo"
        current_datetime = time.strftime(DATE_TIME_FMT)
        report.write(report_default_header(title, int(pos_id), user_id, period, current_datetime, self.store_id))
        self._hourly_sales_report_body(model, user_id, period, report)

        return report.getvalue()

    def _hourly_sales_report_body(self, model, user_id, period, report):
        year = int(period[:4])
        month = int(period[4:6])
        day = int(period[6:])

        grouped_intervals, interval_in_minutes = self._get_configurations(day, month, year)
        intervals_sale_type = []

        start_date = datetime.datetime(year, month, day).replace(tzinfo=tz.tzlocal())
        start_date_utc = convert_from_localtime_to_utc(start_date)
        end_date = start_date + datetime.timedelta(days=1)
        end_date_utc = convert_from_localtime_to_utc(end_date)

        orders = self.order_repository.get_sales_by_date(user_id, start_date_utc, end_date_utc)

        report.write(center("Intervalo de " + str(interval_in_minutes) + " minutos"))
        report.write(empty_line())
        report.write(add_table_line(self.hourly_header, self.hourly_columns_height, self.houry_align))

        self._write_hourly_lines(end_date, grouped_intervals, interval_in_minutes, intervals_sale_type, model, orders,
                                 report, start_date)

        report.write(double_line_separator())

        self._write_intervals_lines(grouped_intervals, None, intervals_sale_type, model, report)

    def _write_intervals_lines(self, grouped_intervals, interval, intervals_sale_type, model, report):
        for grouped_interval in grouped_intervals:
            report.write(center(grouped_interval.name + " [" + grouped_interval.start_time.time().strftime(
                '%H:%M') + " - " + grouped_interval.end_time.time().strftime('%H:%M') + "]"))
            report.write(add_table_line(self.grouped_header, self.grouped_columns_height, self.houry_align))

            orders = grouped_interval.orders
            total_sold_amount, total_sold_orders = self._write_lines(interval, model, orders, report,
                                                                     intervals_sale_type, False)

            total_sold_average = 0 if total_sold_orders == 0 else total_sold_amount / total_sold_orders
            line = ["Total", total_sold_amount, total_sold_orders, total_sold_average]
            report.write(add_table_line(line, self.grouped_columns_height, self.houry_align, self.grouped_format_type))
            report.write(single_line_separator())

    def _write_hourly_lines(self, end_date, grouped_intervals, interval_in_minutes, intervals_sale_type, model, orders,
                            report, start_date):
        intervals = self._get_intervals(start_date, end_date, grouped_intervals, interval_in_minutes, orders)
        for interval, orders in intervals.items():
            sale_types = []

            for order in orders:
                if order.sale_type not in sale_types:
                    sale_types.append(order.sale_type)
                if order.sale_type not in intervals_sale_type:
                    intervals_sale_type.append(order.sale_type)

            total_sold_amount, total_sold_orders = self._write_lines(interval, model, orders, report, sale_types, True)

            if total_sold_amount > 0:
                total_sold_average = 0 if total_sold_orders == 0 else total_sold_amount / total_sold_orders
                line = ["Total", interval, total_sold_amount, total_sold_orders, total_sold_average]
                report.write(add_table_line(line, self.hourly_columns_height, self.houry_align, self.houry_format_type))
                report.write(empty_line())

    def _write_lines(self, interval, model, orders, report, sale_types, hourly_lines):
        total_sold_amount = 0
        total_sold_orders = 0
        for sale_type in sale_types:
            sale_type_orders = [order for order in orders if order.sale_type == sale_type]
            sale_type_sold_amount = sum(order.amount for order in sale_type_orders)
            sale_type_sold_orders = len(sale_type_orders)
            sale_type_average = 0

            if sale_type_sold_orders != 0:
                sale_type_average = sale_type_sold_amount / sale_type_sold_orders

            total_sold_amount += sale_type_sold_amount
            total_sold_orders += sale_type_sold_orders

            if sale_type_sold_amount > 0:
                translated_sale_type = sysactions.translate_message(model, sale_type)

                if hourly_lines:
                    line = [translated_sale_type, interval, sale_type_sold_amount, sale_type_sold_orders,
                            sale_type_average]
                    report.write(add_table_line(line, self.hourly_columns_height, self.houry_align,
                                                self.houry_format_type))
                else:
                    line = [translated_sale_type, sale_type_sold_amount, sale_type_sold_orders, sale_type_average]
                    report.write(add_table_line(line, self.grouped_columns_height, self.houry_align,
                                                self.grouped_format_type))

        return total_sold_amount, total_sold_orders

    @staticmethod
    def _get_intervals(start_date, end_date, grouped_intervals, interval_in_minutes, orders):
        grouped_intervals_processed = False
        intervals = {}
        current_date = start_date
        while current_date < end_date:
            next_date = current_date + datetime.timedelta(minutes=interval_in_minutes)
            interval_key = current_date.time().strftime('%H:%M')
            intervals[interval_key] = []

            for order in orders:
                date = datetime.datetime.strptime(order.timestamp, "%Y-%m-%dT%H:%M:%S")
                date = convert_from_utf_to_localtime(date)
                if current_date <= date < next_date:
                    intervals[interval_key].append(order)

                if not grouped_intervals_processed:
                    for interval in grouped_intervals:
                        if interval.start_time <= date < interval.end_time:
                            interval.orders.append(order)

            grouped_intervals_processed = True
            current_date += datetime.timedelta(minutes=interval_in_minutes)
        intervals = collections.OrderedDict(sorted(intervals.items()))
        return intervals

    @staticmethod
    def _get_configurations(day, month, year):
        config = cfgtools.read(os.environ["LOADERCFG"])
        interval_in_minutes = 30 if config.find_value("HourlySalesReport.IntervalInMinutes") is None \
            else int(config.find_value("HourlySalesReport.IntervalInMinutes"))
        config_intervals = config.find_values("HourlySalesReport.Intervals") or []
        grouped_intervals = []
        try:
            for config in config_intervals:
                name = config.split("|")[0]
                start_hour = int(config.split("|")[1].split(":")[0])
                start_minute = int(config.split("|")[1].split(":")[1])
                end_hour = int(config.split("|")[2].split(":")[0])
                end_minute = int(config.split("|")[2].split(":")[1])
                grouped_intervals.append(IntervalConfiguration(
                    name,
                    datetime.datetime(year, month, day, start_hour, start_minute).replace(tzinfo=tz.tzlocal()),
                    datetime.datetime(year, month, day, end_hour, end_minute).replace(tzinfo=tz.tzlocal()))
                )
        except Exception as _:
            grouped_intervals = []

        return grouped_intervals, interval_in_minutes
