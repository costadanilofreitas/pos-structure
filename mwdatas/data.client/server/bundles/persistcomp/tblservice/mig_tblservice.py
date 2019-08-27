# mig_tblservice.py: resonsible for tblservice schema migration


def migrate(conn, tables):
    updateTablesPriority = ["RestaurantTable", "TableService", "ServiceOrders", "ServiceCustomProperty"]

    for table in updateTablesPriority:
        if tables[table]["fields_OldDB"]:
            strCommonFields = ", ".join(tables[table]["fields_Common"])
            stmt = "INSERT OR REPLACE INTO %s (%s) SELECT %s FROM old.%s;" % (table, strCommonFields, strCommonFields, table)
            conn.query(stmt)
            if table == "Transfer" and "PosId" in tables[table]["fields_Added"]:
                # Special migration for the Transfer.PosId field
                stmt = "UPDATE %s SET PosId=(substr(SessionId, 5,1)) WHERE PosId Is NULL" % (table)
                conn.query(stmt)
