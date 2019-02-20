# -*- coding: utf-8 -*-
def migrate(conn, tables):
    update_tables_priority = ["SapiensData, SapiensDataBkp"]
    for table in update_tables_priority:
        if tables[table]["fields_OldDB"]:
            str_common_fields = ", ".join(tables[table]["fields_Common"])
            stmt = "INSERT OR REPLACE INTO %s (%s) SELECT %s FROM old.%s;" % (table, str_common_fields, str_common_fields, table)
            conn.query(stmt)
