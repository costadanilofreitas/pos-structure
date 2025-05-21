# -*- coding: utf-8 -*-
import json
from datetime import datetime

from actions.models import GLAccount, TransferType
from old_helper import BaseRepository
from actions.util import get_drawer_initial_amount

class AccountRepository(BaseRepository):
    def __init__(self, mbcontext):
        super(AccountRepository, self).__init__(mbcontext)

    def insert_close_operator_info(self, pos_id, inserted_values, cash_envelope_number, session, transfer_type,
                                   database_payments_amount, manager_id, period):
        def inner_func(conn):
            total_bordereau_difference = 0
            initial_fund = get_drawer_initial_amount(pos_id, session)
            for value in inserted_values:
                amount = float(value["amount"])
                tender_id = int(value["tenderId"])
                has_payment = str(tender_id) in database_payments_amount
                sold_amount = 0.0 if not has_payment else database_payments_amount[str(tender_id)]
                envelope_number = ""

                if tender_id == 0:
                    envelope_number = cash_envelope_number

                if amount != sold_amount:
                    if tender_id == 0:
                        total_bordereau_difference += (amount - sold_amount) - initial_fund
                    else:
                        total_bordereau_difference += amount - sold_amount

                gl_account = GLAccount(manager=manager_id, envelope=envelope_number)
                gl_account_json = json.dumps(gl_account, default=lambda o: o.__dict__, sort_keys=True)

                conn.query("""INSERT INTO Transfer VALUES ('{}', {}, '{}', {}, '{}', {}, {}, '{}', '{}')"""
                           .format(period, pos_id, session, TransferType.DECLARED_AMOUNT.value, "DECLARED_AMOUNT",
                                   amount, tender_id, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), gl_account_json))

                conn.query("""INSERT INTO Transfer VALUES ('{}', {}, '{}', {}, '{}', {}, {}, '{}', '{}')"""
                           .format(period, pos_id, session, TransferType.TRANSFER_SKIM.value, "TRANSFER_SKIM",
                                   sold_amount, tender_id, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), ""))

            return total_bordereau_difference

        return self.execute_with_transaction(inner_func, db_name=str(pos_id))

    def update_justification(self, pos_id, session, justification):
        def inner_func(conn):
            conn.query("""UPDATE Transfer
                          SET GLAccount = REPLACE(GLAccount, '"justification": ""', '"justification": "{}"')
                          WHERE SessionId = '{}' AND GLAccount IS NOT NULL AND GLAccount != '' AND Type IN (5,6)"""
                       .format(justification, session))

        self.execute_with_transaction(inner_func, db_name=str(pos_id))

    def get_closing_operator_sessions(self, pos_id, user, start_date, end_date):
        def inner_func(conn):
            sessions = []
            query = """SELECT SessionId
                       FROM Transfer
                       WHERE SessionId LIKE '%user={},%' and Period >= '{}' and Period <= '{}'
                       GROUP BY SessionId
                       ORDER BY Period DESC""".format(user, start_date, end_date)

            cursor = conn.select(query)
            if cursor.rows() > 0:
                for row in cursor:
                    sessions.append(row.get_entry("SessionId"))

            return sessions

        return self.execute_with_connection(inner_func, db_name=str(pos_id))
