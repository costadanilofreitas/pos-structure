import production.repository

from mw_helper import BaseRepository
from persistence import Connection
from typing import List, Tuple, Dict


class ProductRepository(BaseRepository, production.repository.ProductRepository):
    def __init__(self, mb_context):
        super(ProductRepository, self).__init__(mb_context)

    def get_part_codes_of_jit_lines(self, jit_lines):
        # type: (List[str]) -> List[int]
        if len(jit_lines) == 0:
            return []

        def func(conn):
            # type: (Connection) -> List[int]
            param = ""
            for line in jit_lines:
                param += "'" + line + "',"
            param = param[:-1]
            cursor = conn.select(get_part_codes_of_jit_lines_query.format(param))
            part_codes = []
            for row in cursor:
                part_codes.append(int(row.get_entry(0)))

            return part_codes

        return self.execute_with_connection(func)

    def get_combos_to_keep(self):
        def func(conn):
            # type: (Connection) -> List[int]
            cursor = conn.select(get_combos_to_keep_query)
            part_codes = []
            for row in cursor:
                part_codes.append(int(row.get_entry(0)))

            return part_codes

        return self.execute_with_connection(func)

    def get_master_product_map(self):
        def func(conn):
            # type: (Connection) -> Dict[int, Tuple[int, str]]
            cursor = conn.select(get_master_product_map_query)
            master_product_map = {}
            for row in cursor:
                part_code = int(row.get_entry(0))
                master_part_code = int(row.get_entry(1))
                master_product_name = row.get_entry(2).decode("utf-8")

                master_product_map[part_code] = (master_part_code, master_product_name)

            return master_product_map

        return self.execute_with_connection(func)

    def get_prep_times(self):
        def func(conn):
            # type: (Connection) -> Dict[int, int]
            cursor = conn.select(get_prep_time_query)
            prep_time_dict = {}
            for row in cursor:
                part_code = int(row.get_entry(0))
                prep_time = int(row.get_entry(1))

                prep_time_dict[part_code] = prep_time

            return prep_time_dict

        return self.execute_with_connection(func)

    def get_courses_products(self):
        def func(conn):
            # type: (Connection) -> Dict[int, int]
            cursor = conn.select(course_query)
            course_dict = {}
            for row in cursor:
                part_code = int(row.get_entry(0))
                course = row.get_entry(1)

                if course not in course_dict:
                    course_dict[course] = []
                course_dict[course].append(part_code)

            return course_dict

        return self.execute_with_connection(func)

    def get_not_show_on_kitchen(self):
        def func(conn):
            # type: (Connection) -> Dict[int, int]
            cursor = conn.select(not_show_on_kitchen_query)
            ret = []
            for row in cursor:
                ret.append(int(row.get_entry(0)))

            return ret

        return self.execute_with_connection(func)

    def get_no_jit_part_codes(self):
        def func(conn):
            # type: (Connection) -> Dict[int, int]
            cursor = conn.select(no_jit_query)
            ret = []
            for row in cursor:
                ret.append(int(row.get_entry(0)))

            return ret

        return self.execute_with_connection(func)

    def get_cfh_items(self):
        def func(conn):
            # type: (Connection) -> Dict[int, int]
            cursor = conn.select(cfh_items_query)
            ret = []
            for row in cursor:
                ret.append(int(row.get_entry(0)))

            return ret

        return self.execute_with_connection(func)

    def get_product_points(self):
        def func(conn):
            # type: (Connection) -> Dict[int, int]
            cursor = conn.select(item_points_query)
            ret = {}
            for row in cursor:
                ret[int(row.get_entry(0))] = int(row.get_entry(1))

            return ret

        return self.execute_with_connection(func)


get_part_codes_of_jit_lines_query = """
SELECT ProductCode
FROM 
productdb.Production 
where (Expiration is null or Expiration > DATETIME('now')) and JITLines in ({})
"""

get_combos_to_keep_query = """
SELECT ProductCode
FROM 
productdb.ProductCustomParams 
where (CustomParamId = 'SHOW_ON_JIT')
"""

get_master_product_map_query = """
select t.ProductCode, t.CustomParamValue, p.ProductName from 
(
SELECT ProductCode, CustomParamValue
FROM 
ProductCustomParams 
where (CustomParamId = 'KDS_MASTER_PART_CODE')
) t inner join Product p on t.CustomParamValue = p.ProductCode
"""

get_prep_time_query = """
select ProductCode, CustomParamValue from ProductCustomParams where CustomParamId = 'PrepTime'
"""


course_query = """
select ProductCode, CustomParamValue from ProductCustomParams where CustomParamId = 'Course'
"""

not_show_on_kitchen_query = """
SELECT p.ProductCode
FROM Production p
JOIN ProductKernelParams pkp ON pkp.ProductCode = p.ProductCode
JOIN ProductType pt ON pt.TypeId = pkp.ProductType
WHERE ShowOnKitchen == 0 AND pt.TypeDescr <> 'TYPE_OPTION'
"""

no_jit_query = """
select ProductCode from Production where JITLines is NULL and ShowOnKitchen = 1
"""

cfh_items_query = """
 SELECT ProductCode FROM ProductTags
WHERE LOWER(Tag) = 'cfh=true'
UNION
SELECT ProductCode FROM ProductCustomParams
WHERE LOWER(CustomParamId) = 'cfh' AND LOWER(CustomParamValue) = 'true'
"""


item_points_query = """
SELECT ProductCode, CustomParamValue from ProductCustomParams where CustomParamId = 'ProductionPoints'
"""
