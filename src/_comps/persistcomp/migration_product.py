# import os
# import sys
#
# debugPath = 'C:\Program Files\JetBrains\PyCharm 2019.2\debug-eggs\pydevd-pycharm.egg'
# if os.path.exists(debugPath):
#     try:
#         sys.path.index(debugPath)
#     except:
#         sys.path.append(debugPath)
#     import pydevd


def migrate(conn, tables):
    # pydevd.settrace('localhost', port=9165, stdoutToServer=True, stderrToServer=True, suspend=True)

    update_tables_priority = [
        "Product", "ProductClassification", "ProductPart", "PriceList", "Price", "ModifierQtyLabels", "Dimensions",
        "DimensionGroups", "ProductKernelParams", "ProductCustomParams", "ProductTags", "Production", "PromoRule",
        "Navigation", "ProductNavigation", "NavigationCustomParams", "ProductNavigationCustomParams", "Descriptions",
        "ProductDescriptions", "NavigationDescriptions", "CurrencyExchange", "TenderType", "ProductXREF"
    ]

    for table in update_tables_priority:
        if tables[table]["fields_OldDB"] and len(tables[table]["fields_Common"]) > 0:
            str_common_fields = ", ".join(tables[table]["fields_Common"])
            insert_str = "INSERT OR REPLACE INTO {} ({}) SELECT {} FROM old.{};"
            stmt = insert_str.format(table, str_common_fields, str_common_fields, table)
            conn.query(stmt)
