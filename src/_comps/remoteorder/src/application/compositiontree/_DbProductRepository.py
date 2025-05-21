# -*- coding: utf-8 -*-
import json

from application.compositiontree import ProductRepository, ProductPart
from msgbus import MBEasyContext
from persistence import Driver
from typing import List, Dict


class DbProductRepository(ProductRepository):
    def __init__(self, mbcontext):
        # type: (MBEasyContext) -> None
        super(DbProductRepository, self).__init__()
        self.mbcontext = mbcontext

    def get_all_combo_products(self):
        # type: () -> Dict[unicode, List[ProductPart]]
        return self._get_combo_sons(0)

    def get_all_combo_options(self):
        # type: () -> Dict[unicode, List[ProductPart]]
        ret = self._get_option_from_qty_options(2)
        return ret

    def get_all_combo_combos(self):
        # type: () -> Dict[unicode, List[ProductPart]]
        return self._get_combo_sons(2)

    def get_all_option_products(self):
        # type: () -> Dict[unicode, List[ProductPart]]
        conn = None
        try:
            conn = Driver().open(self.mbcontext)

            option_ingredient_tuples = [(x.get_entry(0).encode("utf-8"), x.get_entry(1).encode("utf-8"))
                                        for x in conn.select("""select ClassCode, ProductCode from ProductClassification where ClassCode <> 1""")]

            option_item_qtys_tag = [(x.get_entry(0).encode("utf-8"), x.get_entry(1).encode("utf-8"))
                                    for x in conn.select("""select ProductCode, Tag from ProductTags where Tag like 'ItemQtys=%'""")]

            option_qty_dict = {}
        finally:
            if conn:
                conn.close()

        def convert_tag_qty_tuples(option_item_qty_tag):
            option_code = option_item_qty_tag[0]
            tag_value = option_item_qty_tag[1]
            qtys = tag_value.split("=")[1].split(";")
            option_qty_dict[option_code] = (int(qtys[0]), int(qtys[1]))

        map(convert_tag_qty_tuples, option_item_qtys_tag)
        option_code_ingredient_list = {}

        def group_products_in_same_option(item):
            option_code = item[0]
            product_code = item[1]
            if option_code in option_code_ingredient_list:
                ingredient_list = option_code_ingredient_list[option_code]
            else:
                ingredient_list = []
                option_code_ingredient_list[option_code] = ingredient_list

            product_part = ProductPart()
            product_part.parent_part_code = option_code
            product_part.part_code = product_code
            product_part.min_qty = 0
            product_part.max_qty = 1
            if option_code in option_qty_dict:
                product_part.min_qty = option_qty_dict[option_code][0]
                product_part.max_qty = option_qty_dict[option_code][1]

            ingredient_list.append(product_part)

        map(group_products_in_same_option, option_ingredient_tuples)

        return option_code_ingredient_list

    def get_all_product_ingredients(self):
        # type: () -> Dict[unicode, List[ProductPart]]
        products_ingredients_by_tag = self.get_products_ingredients_by_tag()
        products_ingredients_by_parts = self.get_products_ingredients_by_parts()

        merged_products = self.merge_products_ingredients(products_ingredients_by_tag, products_ingredients_by_parts)
        return self._filter_dt_only_products(merged_products)

    def get_products_ingredients_by_tag(self):
        return self._get_option_from_qty_options(0)

    def get_products_ingredients_by_parts(self):
        conn = None
        products_parts = {}
        try:
            conn = Driver().open(self.mbcontext)
            all_parts = conn.select("""select * from ProductPart order by ProductCode""")
            for part in all_parts:
                product_part = ProductPart()
                product_part.parent_part_code = str(part.get_entry("ProductCode"))
                product_part.part_code = str(part.get_entry("PartCode"))
                product_part.default_qty = int(part.get_entry("DefaultQty"))
                product_part.min_qty = int(part.get_entry("MinQty"))
                product_part.max_qty = int(part.get_entry("MaxQty"))

                if product_part.parent_part_code in products_parts:
                    products_parts[product_part.parent_part_code].append(product_part)
                else:
                    products_parts[product_part.parent_part_code] = [product_part]
        except Exception as _:
            pass
        finally:
            if conn:
                conn.close()

        return products_parts

    @staticmethod
    def merge_products_ingredients(by_tags, by_parts):
        products_ingredients = by_tags.copy()
        products_ingredients.update(by_parts)
        return products_ingredients

    def get_all_combos(self):
        # type: () -> Dict[unicode, unicode]
        conn = None
        try:
            conn = Driver().open(self.mbcontext)
            ret = {str(x.get_entry(0)): str(x.get_entry(0)) for x in conn.select("select ProductCode from ProductKernelParams where ProductType = 2")}
        finally:
            if conn:
                conn.close()

        return ret

    def get_all_options(self):
        # type: () -> Dict[unicode, unicode]
        conn = None
        try:
            conn = Driver().open(self.mbcontext)
            ret = {str(x.get_entry(0)): str(x.get_entry(0)) for x in conn.select("select ProductCode from ProductKernelParams where ProductType = 1")}
        finally:
            if conn:
                conn.close()

        return ret

    def get_all_products(self):
        # type: () -> Dict[unicode, unicode]
        conn = None
        try:
            conn = Driver().open(self.mbcontext)
            ret = {str(x.get_entry(0)): str(x.get_entry(0)) for x in conn.select("select ProductCode from ProductKernelParams where ProductType = 0")}
        finally:
            if conn:
                conn.close()

        return ret

    def get_default_products(self):
        # type: () -> Dict[unicode, List[ProductPart]]
        default_products_by_tags = self.get_default_products_by_tags()
        default_products_by_part = self.get_default_products_by_part()
        return self.merge_products_ingredients(default_products_by_tags, default_products_by_part)

    def get_default_products_by_tags(self):
        # type: () -> Dict[(int, int), Dict[int, int]]
        conn = None
        try:
            conn = Driver().open(self.mbcontext)

            default_products_tags = [(unicode(x.get_entry(0)), unicode(x.get_entry(1))) for x in conn.select("""select pkp.ProductCode, pt.Tag
            from
            ProductKernelParams pkp
            inner join ProductTags pt
            on pkp.ProductCode = pt.ProductCode
            and (Tag like 'HasOptions=%' or Tag like 'Ingredients=%')""")]

            # TagTamplate: HasOptions|Ingredients=OptionCode1>ProductCode1;ProductCode2;OptionCode2>ProductCode1
            ret = {}
            for tag_tuple in default_products_tags:
                product_code = tag_tuple[0]
                tag = tag_tuple[1]
                tag_value = tag.split('=')[1]

                options_list = tag_value.split("|")

                for option in options_list:
                    option_code = option.split(">")[0]
                    product_list = option.split(">")[1].split(";")
                    for product in product_list:
                        key = (product_code, option_code)
                        if key in ret:
                            inner_dict = ret[key]
                        else:
                            inner_dict = {}
                            ret[key] = inner_dict

                        inner_dict[product] = product
        finally:
            if conn:
                conn.close()

        return ret

    def get_default_products_by_part(self):
        # type: () -> Dict[(int, int), Dict[int, int]]
        conn = None
        try:
            conn = Driver().open(self.mbcontext)
            query = """
                        SELECT ProductPart.ProductCode, partCode, CustomParamValue
                        FROM ProductCustomParams JOIN ProductPart
                        ON ProductCustomParams.ProductCode = ProductPart.ProductCode
                        WHERE CustomParamId = 'defaultoption'
                    """

            default_products_tags = [(unicode(x.get_entry(0)), unicode(x.get_entry(1)), unicode(x.get_entry(2))) for x in conn.select(query)]

            # TagTamplate: ProductCode1|ProductCode2
            ret = {}
            for tag_tuple in default_products_tags:
                product_code = tag_tuple[0]
                part_code = tag_tuple[1]
                tag_value = tag_tuple[2]

                product_list = tag_value.split("|")
                for product in product_list:
                    key = (product_code, part_code)
                    if key in ret:
                        inner_dict = ret[key]
                    else:
                        inner_dict = {}
                        ret[key] = inner_dict
                    inner_dict[product] = product

            query = """SELECT ProductCode, PartCode, CustomAttr FROM productpart WHERE customattr LIKE '%defaultOption%'"""
            default_products_tags = [(unicode(x.get_entry(0)), unicode(x.get_entry(1)), unicode(x.get_entry(2))) for x in conn.select(query)]

            # TagTamplate: {"defaultOption":"Product1|Product2"}
            for tag_tuple in default_products_tags:
                product_code = tag_tuple[0]
                part_code = tag_tuple[1]
                tag_value = json.loads(tag_tuple[2])

                product_list = tag_value["defaultOption"].split("|")
                for product in product_list:
                    key = (product_code, part_code)
                    if key in ret:
                        inner_dict = ret[key]
                    else:
                        inner_dict = {}
                        ret[key] = inner_dict
                    inner_dict[product] = product
        finally:
            if conn:
                conn.close()

        return ret

    def get_product_name_dictionary(self):
        # type: () -> Dict[unicode, unicode]
        conn = None
        try:
            conn = Driver().open(self.mbcontext)
            ret = {str(x.get_entry(0)): str(x.get_entry(1)) for x in conn.select("select ProductCode, ProductName from Product")}
        finally:
            if conn:
                conn.close()

        return ret

    def get_unavailable_products(self):
        # type: () -> List[unicode]
        conn = None
        try:
            conn = Driver().open(self.mbcontext)
            return [x.get_entry(0) for x in conn.select("SELECT ProductCode FROM rupturadb.RupturaItens WHERE EnableDate IS NULL;")]
        finally:
            if conn:
                conn.close()

    def _get_option_from_qty_options(self, product_type):
        # type: (int) -> Dict[unicode, List[ProductPart]]
        conn = None
        try:
            conn = Driver().open(self.mbcontext)

            all_products_qty_options_tag = {unicode(x.get_entry(0)): unicode(x.get_entry(1)) for x in conn.select("""select pkp.ProductCode, pt.Tag
            from
            ProductKernelParams pkp
            inner join ProductTags pt
            on pkp.ProductCode = pt.ProductCode
            where ProductType = %d
            and Tag like 'QtyOptions=%%'""" % product_type)}

            # TagTemplate OptionCode1>DefaultQty;MinQty;MaxQty|OptionCode2>DefaultQty;MinQty;MaxQty
            ret = {}
            for product_code in all_products_qty_options_tag.keys():
                qty_options_tag = all_products_qty_options_tag[product_code]  # type: unicode
                if len(qty_options_tag.split("=")) > 1:
                    tag_value = qty_options_tag.split("=")[1]
                    all_ingredients = tag_value.split("|")

                    if product_code in ret:
                        product_ingredient_list = ret[product_code]
                    else:
                        product_ingredient_list = []
                        ret[product_code] = product_ingredient_list

                    for ingredient_info in all_ingredients:
                        ingredient_part_code = ingredient_info.split(">")[0]
                        ingredient_qtys = ingredient_info.split(">")[1]

                        product_part = ProductPart()
                        product_part.parent_part_code = product_code
                        product_part.part_code = ingredient_part_code
                        product_part.min_qty = int(ingredient_qtys.split(";")[1])
                        product_part.max_qty = int(ingredient_qtys.split(";")[2])

                        product_ingredient_list.append(product_part)
        finally:
            if conn:
                conn.close()

        return ret

    def _filter_dt_only_products(self, merged_products):
        conn = None
        try:
            conn = Driver().open(self.mbcontext)
            query = """select ProductCode, Tag from ProductTags where Tag like 'DTOnly=%'"""
            dt_only_options_list = [(unicode(x.get_entry(0)), unicode(x.get_entry(1))) for x in conn.select(query)]
            dt_product_option_list_dict = {}
            
            for product_tag in dt_only_options_list:
                part_code = product_tag[0]
                tag = product_tag[1]
            
                tag_value = tag[7:]
                tag_options_list = tag_value.split("|")
            
                if part_code in dt_product_option_list_dict:
                    product_option_dict = dt_product_option_list_dict[part_code]
                else:
                    product_option_dict = {}
                    dt_product_option_list_dict[part_code] = product_option_dict
            
                for option_part_code in tag_options_list:
                    product_option_dict[option_part_code] = option_part_code
        
                for product_code in dt_product_option_list_dict:
                    iterable_merged_products = merged_products
                    if product_code not in iterable_merged_products:
                        continue
                        
                    for banned_product in dt_product_option_list_dict[product_code]:
                        for son_product in iterable_merged_products[product_code]:
                            if son_product.part_code == banned_product:
                                merged_products[product_code].remove(son_product)

        except Exception as _:
            pass
        finally:
            if conn:
                conn.close()

        return merged_products

    def _get_combo_sons(self, part_type):
        # type: (int) -> Dict[unicode, List[ProductPart]]

        conn = None
        try:
            conn = Driver().open(self.mbcontext)

            combo_products_list = [(unicode(x.get_entry(0)), unicode(x.get_entry(1)), int(x.get_entry(2)), int(x.get_entry(3)), int(x.get_entry(4)))
                                   for x in conn.select("""
            select pp.ProductCode, pp.PartCode, pp.MinQty, pp.MaxQty, pp.DefaultQty
            from ProductPart pp
            inner join ProductKernelParams pkp
            on pp.ProductCode = pkp.ProductCode
            where pkp.ProductType = 2 and pp.PartType = {}""".format(part_type))]

            combo_products_dict = {}

            def convert_tuple_dictionary(product_tuple):
                combo_part_code = product_tuple[0]
                product_part_code = product_tuple[1]
                min_qty = product_tuple[2]
                max_qty = product_tuple[3]
                default_qty = product_tuple[4]

                if combo_part_code in combo_products_dict:
                    product_list = combo_products_dict[combo_part_code]
                else:
                    product_list = []
                    combo_products_dict[combo_part_code] = product_list

                product_part = ProductPart()
                product_part.part_code = product_part_code
                product_part.min_qty = min_qty
                product_part.max_qty = max_qty
                product_part.default_qty = default_qty

                product_list.append(product_part)

            map(convert_tuple_dictionary, combo_products_list)
        finally:
            if conn:
                conn.close()

        return combo_products_dict
