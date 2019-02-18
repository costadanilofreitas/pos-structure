def migrate(conn, tables):
    updateTablesPriority = [
        "FiscalPrinters", "FiscalOrders", "FiscalOrderItems",
        "FiscalOrderTender", "NonFiscalDocuments", "NonFiscalDocumentTenders",
        "ZTapes", "ZTapeTotalizers", "NotasManuais", "ElectronicTransactions",
        "Estoque", "EstoqueHistorico", "Insumos"
    ]
    conn.query("DELETE FROM FiscalDEnabled;")
    for table in updateTablesPriority:
        strCommonFields = ", ".join(tables[table]["fields_Common"])
        stmt = "INSERT OR REPLACE INTO %s (%s) SELECT %s FROM old.%s;" % (table, strCommonFields, strCommonFields, table)
        conn.query(stmt)
    conn.query("INSERT INTO FiscalDEnabled(Enabled) VALUES(1);")
