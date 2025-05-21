import orderpump.repository
from mwhelper import BaseRepository


class ProductRepository(orderpump.repository.ProductRepository, BaseRepository):
    def __init__(self, mb_context):
        super(ProductRepository, self).__init__(mb_context)
        self.category_cache = {}
        self.sub_category_cache = {}

        def handle_cursor(cursor):
            for row in cursor:
                product_code = int(row.get(0))
                param_id = row.get(1)
                param_value = row.get(2)

                if param_id == "Categories":
                    self.category_cache[product_code] = param_value
                else:
                    self.sub_category_cache[product_code] = param_value

        def get_categories_from_tags(conn):
            handle_cursor(conn.select(category_from_tags_query))

        def get_categories_from_custom_params(conn):
            handle_cursor(conn.select(category_from_custom_params))

        self.execute_with_connection(get_categories_from_tags)
        self.execute_with_connection(get_categories_from_custom_params)

    def get_category(self, part_code):
        if part_code in self.category_cache:
            return self.category_cache[part_code]
        return ""

    def get_sub_category(self, part_code):
        if part_code in self.sub_category_cache:
            return self.sub_category_cache[part_code]
        return ""


category_from_tags_query = """
SELECT ProductCode, CustomParamId, CustomParamValue
FROM (
    SELECT
        ProductCode,
        substr(Tag,1,instr(Tag,'=')-1) AS CustomParamId,
        substr(Tag,instr(Tag,'=')+1) AS CustomParamValue
    FROM ProductTags
) Tags
WHERE Tags.CustomParamId IN ('Categories', 'SubCategories')
"""


category_from_custom_params = """
SELECT ProductCode, CustomParamId, CustomParamValue 
FROM ProductCustomParams 
WHERE CustomParamId IN ('Categories', 'SubCategories')
"""
