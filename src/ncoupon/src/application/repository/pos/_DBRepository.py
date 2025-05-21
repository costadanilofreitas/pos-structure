from datetime import datetime, timedelta

import iso8601
from application.model import \
    BenefitControllerDto, \
    OperationStatus, \
    BenefitAppliers, \
    OperationDescription
from application.model.configuration import Configurations
from mbcontextmessagehandler import MbContextMessageBus
from mwhelper import BaseRepository
from persistence import Connection
from typing import List, Optional


class DBRepository(BaseRepository):

    def __init__(self, configs, message_bus):
        # type: (Configurations, MbContextMessageBus) -> None

        super(DBRepository, self).__init__(message_bus.mbcontext)

        self.logger = configs.logger
        self.configs = configs
        self.message_bus = message_bus

    def manage_operation_status(self, success, benefit_id, pos_id, operation_description, benefit_applier, retry_quantity):
        # type: (bool, str, int, OperationDescription, BenefitAppliers, int) -> None

        if success:
            self.delete_pending_operation(benefit_id, pos_id)
        else:
            retry_quantity += 1

            if retry_quantity > self.configs.max_retry_quantity:
                message = "The benefit has exceeded the max retry quantity. CouponId: {}; RetryQuantity: {}" \
                    .format(benefit_id, retry_quantity)
                self.logger.info(message)

            self.insert_or_update_pending_operation(benefit_id,
                                                    pos_id,
                                                    operation_description,
                                                    OperationStatus.NOT_DONE,
                                                    benefit_applier,
                                                    retry_quantity)

    def find_pending_operations(self):
        # type: () -> Optional[List[BenefitControllerDto]]

        def inner_func(conn):
            # type: (Connection) -> Optional[List[BenefitControllerDto]]

            query = "SELECT * FROM PendingOperations WHERE OperationStatusId = '{}'".format(OperationStatus.NOT_DONE)
            cursor = conn.select(query)
            if not cursor.rows():
                return

            utc_now = iso8601.parse_date(datetime.utcnow().isoformat())
            acceptable_datetime_limit = timedelta(seconds=self.configs.retry_min_time_to_try_again)

            results = []
            for result in cursor:
                benefit = BenefitControllerDto()
                benefit.benefit_id = result.get_entry("BenefitId")
                benefit.pos_id = result.get_entry("PosId")
                benefit.operation_description = int(result.get_entry("OperationDescriptionId"))
                benefit.benefit_applier = result.get_entry("BenefitApplier")
                benefit.retry_quantity = int(result.get_entry("RetryQuantity"))
                benefit.last_retry_date_utc = iso8601.parse_date(result.get_entry("LastRetryDateUTC"))

                exceed_acceptable_datetime_limit = benefit.last_retry_date_utc + acceptable_datetime_limit > utc_now
                exceed_acceptable_max_retry_quantity = benefit.retry_quantity > self.configs.max_retry_quantity
                if exceed_acceptable_datetime_limit or exceed_acceptable_max_retry_quantity:
                    continue

                results.append(benefit)

            return results

        return self.execute_with_connection(inner_func, service_name=self.configs.persistence_name)

    def get_benefit_applier_by_db(self, benefit_id, pos_id):
        # type: (str, int) -> Optional[BenefitAppliers]

        def inner_func(conn):
            # type: (Connection) -> Optional[BenefitAppliers]

            query = "SELECT BenefitApplier FROM PendingOperations WHERE BenefitId = '{0}' AND PosId = '{1}'"\
                .format(benefit_id, pos_id)
            cursor = conn.select(query)
            if not cursor.rows():
                return

            return cursor.get_row(0).get_entry(0)

        return self.execute_with_connection(inner_func, service_name=self.configs.persistence_name)

    def insert_or_update_pending_operation(self, benefit_id, pos_id, operation_description, operation_status, benefit_applier, retry_quantity):
        # type: (str, int, OperationDescription, OperationStatus, BenefitAppliers, int) -> None

        def inner_func(conn):
            # type: (Connection) -> None

            last_retry_date = datetime.utcnow().isoformat()

            query = "INSERT OR REPLACE INTO PendingOperations(" \
                    "BenefitId, " \
                    "PosId, " \
                    "OperationDescriptionId, " \
                    "OperationStatusId, " \
                    "BenefitApplier, " \
                    "RetryQuantity, " \
                    "LastRetryDateUTC) " \
                    "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')"
            query = query.format(benefit_id,
                                 pos_id,
                                 operation_description,
                                 operation_status,
                                 benefit_applier,
                                 retry_quantity,
                                 last_retry_date)
            conn.query(query)

        self.execute_with_transaction(inner_func, service_name=self.configs.persistence_name)

    def delete_pending_operation(self, benefit_id, pos_id):
        # type: (str, int) -> None

        def inner_func(conn):
            # type: (Connection) -> None

            query = "DELETE FROM PendingOperations WHERE BenefitId = '{0}' AND PosId = '{1}'"\
                .format(benefit_id, pos_id)
            conn.query(query)

        self.execute_with_transaction(inner_func, service_name=self.configs.persistence_name)
