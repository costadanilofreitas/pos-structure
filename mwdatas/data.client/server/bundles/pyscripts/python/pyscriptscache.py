# -*- coding: utf-8 -*-
import persistence
import pyscripts
import copy
import sys
import os

from xml.etree.ElementTree import Element
from xml.etree import cElementTree as eTree
from cache import CacheManager, PeriodBasedExpiration
from typing import Optional


debugPath = '../python/pycharm-debug.egg'
if os.path.exists(debugPath):
    try:
        sys.path.index(debugPath)
    except:
        sys.path.append(debugPath)
    import pydevd

# Use the line below in the function you want to debug
# pydevd.settrace('localhost', port=9123, stdoutToServer=True, stderrToServer=True)
# UNTIL HERE


class ModifierSets:
    def __init__(self):
        self.context = ""
        self.level = -1
        self.line_number = -1
        self.modifiers_sets = {}

    def to_xml(self):
        element = eTree.Element("ModifierSets")  # type: Element

        element.set("itemId", self.context.decode("UTF-8"))
        element.set("level", str(self.level))
        element.set("lineNumber", str(self.line_number))

        for modifier_key in self.modifiers_sets:
            element.append(self.modifiers_sets[modifier_key].to_xml())

        return element


class ModifierSet:
    def __init__(self):
        self.context = ""
        self.part_code = ""
        self.product_name = ""
        self.display_name = ""
        self.default_qty = ""
        self.min_qty = ""
        self.max_qty = ""
        self.min_item_qty = ""
        self.max_item_qty = ""
        self.json_array_tags = ""
        self.modifiers = {}

    def to_xml(self):
        element = eTree.Element("ModifierSet")  # type: Element

        element.set("defaultQty", str(self.default_qty))
        element.set("includedQty", str(self.default_qty))
        element.set("partCode", self.part_code)

        element.set("productName", self.product_name.decode("UTF-8"))
        element.set("displayName", self.display_name.decode("UTF-8"))
        element.set("jsonArrayTags", str(self.json_array_tags))

        element.set("minQty", str(self.min_qty))
        element.set("maxQty", str(self.max_qty))
        element.set("minItemQty", str(self.min_item_qty))
        element.set("maxItemQty", str(self.max_item_qty))

        for modifier_key in self.modifiers:
            element.append(self.modifiers[modifier_key].to_xml())

        return element


class Modifier:
    def __init__(self):
        self.context = ""
        self.part_code = ""
        self.product_name = ""
        self.unit_price = ""
        self.add_price = ""
        self.sub_price = ""
        self.color = ""
        self.def_qty = 0
        self.ord_qty = 0
        self.level = -1
        self.line_number = -1
        self.json_array_tags = ""
        self.parts = []

    def to_xml(self):
        element = eTree.Element("Modifier")  # type: Element

        element.set("itemId", self.context)
        element.set("partCode", self.part_code)

        element.set("productName", self.product_name.decode("UTF-8"))
        element.set("color", self.color)
        element.set("jsonArrayTags", str(self.json_array_tags))

        element.set("addedUnitPrice", str(self.add_price))
        element.set("subUnitPrice", str(self.sub_price))
        element.set("itemPrice", str(self.unit_price))

        element.set("defaultQty", str(self.def_qty))
        element.set("orderedQty", str(self.ord_qty))

        element.set("level", str(self.level))
        element.set("lineNumber", str(self.line_number))

        for part_key in self.parts:
            element.append(self.parts[part_key].to_xml())

        return element


class Part:
    def __init__(self):
        self.context = ""
        self.part_code = ""
        self.product_name = ""
        self.unit_price = ""
        self.add_price = ""
        self.sub_price = ""
        self.def_qty = 0
        self.min_qty = 0
        self.max_qty = 0
        self.level = -1
        self.line_number = -1
        self.json_array_tags = ""

    def to_xml(self):
        element = eTree.Element("Part")  # type: Element

        element.set("itemId", self.context)
        element.set("partCode", self.part_code)
        element.set("productName", self.product_name)
        element.set("jsonArrayTags", str(self.json_array_tags))

        element.set("addedUnitPrice", str(self.add_price))
        element.set("subUnitPrice", str(self.sub_price))
        element.set("itemPrice", str(self.unit_price))

        element.set("defQty", str(self.def_qty))
        element.set("minQty", str(self.min_qty))
        element.set("maxQty", str(self.max_qty))

        element.set("level", str(self.level))
        element.set("lineNumber", str(self.line_number))

        return element


class Cache:
    def __init__(self, mbcontext):
        self.mbcontext = mbcontext
        self._tags_cache = CacheManager(PeriodBasedExpiration(5), new_object_func=self._tags_cache_renewer)
        self._parts_cache = CacheManager(PeriodBasedExpiration(5), new_object_func=self._parts_cache_renewer)
        self._product_prices_cache = CacheManager(PeriodBasedExpiration(5), new_object_func=self._product_prices_cache_renewer)
        self._price_key_cache = CacheManager(PeriodBasedExpiration(5), new_object_func=self._price_key_cache_renewer)
        self._must_modify_cache = CacheManager(PeriodBasedExpiration(5), new_object_func=self._must_modify_cache_renewer)
        self._dt_only_cache = CacheManager(PeriodBasedExpiration(5), new_object_func=self._dt_only_cache_renewer)
        self._discount_cache = CacheManager(PeriodBasedExpiration(5), new_object_func=self._discount_cache_renewer)
        self._options_cache = CacheManager(PeriodBasedExpiration(5), new_object_func=self._options_cache_renewer)

    def seach_items_tree_combo(self, part_code, list_categories=[]):
        """
        Busca na arvore de um combo e retorna o ultimo item da mesma
        :param part_code: product_code ou product_part
        :return: ultimo id da arvore
        """
        tags_cache = self._tags_cache.get_cached_object()
        p_code = [part_code] if len(self.get_parts(part_code)) is 0 else filter(lambda x: x, self.get_parts(part_code))

        if len(p_code) > 1:
            list_items = []

            for code in p_code:
                if len(self.get_parts(code)) is 0:
                    tag_kiosk = tags_cache[code][0]
                    list_items.append(1 if (tag_kiosk.get('CATEGORY', None) in list_categories) else 0)
            return list_items
        else:
            if len(self.get_parts(p_code[0])) is 0:
                tag_kiosk = tags_cache[p_code[0]][0]
                return [1 if (tag_kiosk.get('CATEGORY', None) in list_categories) else 0]

        return self.seach_items_tree_combo(part_code, list_categories)
    # END of seach_items_tree_combo

    def is_not_order_kiosk(self, part_code, podtype, list_categories=[]):
        """
        Verifica se o pedido tem a tag de sobremesas para ser vendido, apenas valido para o POS 8
        :param part_code: id do produto
        :param podtype: Point-of-distribution type
        :return: Boolean
        """
        if podtype == 'KK':
            parts = [part_code] if len(self.get_parts(part_code)) is 0 else self.get_parts(part_code)
            last_items_tree = [self.seach_items_tree_combo(p_code, list_categories) for p_code in parts]
            result = list(set(sum(last_items_tree, [])))

            if not len(result) > 1:
                return True if result[0] is 0 else False
            return True
    # END of is_not_order_kiosk

    def get_tags_as_dict(self, part_code, wanted_tag):
        # type: (str, str) -> str

        tags_cache = self._tags_cache.get_cached_object()

        if wanted_tag:
            wanted_tag = wanted_tag.upper()
            if part_code in tags_cache and wanted_tag in tags_cache[part_code][0]:
                return tags_cache[part_code][0][wanted_tag]
        else:
            if part_code in tags_cache:
                return tags_cache[part_code][0]

        return ''
    # END of get_tags

    def get_tags_as_str(self, part_code):
        # type: (str) -> str

        tags_cache = self._tags_cache.get_cached_object()
        if part_code in tags_cache:
            return tags_cache[part_code][1]

        return ''
    # END of get_tags

    def get_parts(self, part_code):
        # type: (str) -> dict

        parts_cache = self._parts_cache.get_cached_object()
        if part_code in parts_cache:
            return parts_cache[part_code]

        return {}
    # END of get_parts

    def get_options(self, part_code):
        # type: (str) -> Optional[ModifierSet]
        options_cache = self._options_cache.get_cached_object()

        if part_code in options_cache:
            return copy.deepcopy(options_cache[part_code])

        return None
    # END of get_options

    def get_best_price(self, context, part_code, pod_type="EI"):
        # type: (str, str, str) -> Optional(dict)
        best_price, _ = self._get_best_price_and_key(context, part_code, pod_type)
        return best_price

    def get_best_price_key(self, context, part_code, pod_type="EI"):
        # type: (str, str, str) -> Optional(dict)
        _, price_key = self._get_best_price_and_key(context, part_code, pod_type)
        return price_key

    def _get_best_price_and_key(self, context, part_code, pod_type):
        best_price = None
        best_price_key = None

        if pod_type == "DL":
            best_price, best_price_key = self._find_best_price_and_key_by_pod_type(context, part_code, "DL")
        if best_price is None and best_price_key is None:
            best_price, best_price_key = self._find_best_price_and_key_by_pod_type(context, part_code, "EI")

        return best_price, best_price_key

    def _find_best_price_and_key_by_pod_type(self, current_context, part_code, pod_type):
        all_contexts = Cache._get_all_product_contexts(current_context)

        for context in all_contexts:
            price = self._get_price_in_context(context, part_code, pod_type)
            price_key = self._get_price_key_in_context(context, part_code, pod_type)
            if price is not None:
                return price, price_key
        return None, None

    @staticmethod
    def _get_all_product_contexts(current_context):
        contexts = []
        index = 0

        while index >= 0:
            contexts.append(current_context)
            index = current_context.find('.')
            current_context = current_context[index + 1:]

        contexts.append("")
        return contexts

    def _get_price_in_context(self, context, part_code, pod_type):
        key = (part_code, context)
        product_price_cache = self._product_prices_cache.get_cached_object()[pod_type]
        price = product_price_cache[key] if key in product_price_cache else None
        return price

    def _get_price_key_in_context(self, context, part_code, pod_type):
        key = (part_code, context)
        product_price_key_cache = self._price_key_cache.get_cached_object()
        price_key = product_price_key_cache[pod_type][key] if key in product_price_key_cache[pod_type] else None
        return price_key

    def get_must_modify(self, part_code, pod_type):
        must_modify_cache = self._must_modify_cache.get_cached_object()
        dt_only_cache = self._dt_only_cache.get_cached_object()

        if part_code in must_modify_cache:
            if pod_type != "DT" and part_code in dt_only_cache:
                return None
            else:
                return must_modify_cache[part_code]

        return None
    # END get_best_price_key

    def get_discount(self, part_code, discount_code):
        discount_cache = self._discount_cache.get_cached_object()
        key = (part_code, discount_code)
        if key in discount_cache:
            return discount_cache[key]

        return None
    # END get_best_price_key

    def _tags_cache_renewer(self):
        conn = None
        try:
            conn = persistence.Driver().open(self.mbcontext)
            temp_cache = [(x.get_entry(0), x.get_entry(1)) for x in conn.select("""SELECT ProductCode, upper(Tag) FROM productdb.ProductTags ORDER BY ProductCode""")]

            if not temp_cache:
                return {}

            tags_cache = {}
            tags = {}
            tag_str = ""
            current_code = temp_cache[0][0]
            for tags_line in temp_cache:
                if current_code != tags_line[0]:
                    tags_cache[current_code] = (tags, tag_str)
                    current_code = tags_line[0]
                    tags = {}
                    tag_str = ""

                tmp = tags_line[1].split('=')
                tags[tmp[0].upper()] = tmp[1] if len(tmp) > 1 else ''
                tag_str = tag_str + tags_line[1]

            tags_cache[current_code] = (tags, tag_str)
            return tags_cache
        finally:
            if conn:
                conn.close()

    def _parts_cache_renewer(self):
        conn = None
        try:
            conn = persistence.Driver().open(self.mbcontext)
            temp_cache = [(x.get_entry(0), x.get_entry(1), (x.get_entry(2), x.get_entry(3), x.get_entry(4), x.get_entry(5))) for x in
                          conn.select("""SELECT ProductPart.ProductCode, ProductPart.PartCode, DefaultQty, MinQty, MaxQty, ProductName FROM ProductPart INNER JOIN Product ON ProductPart.PartCode = Product.ProductCode WHERE PartType != 1 ORDER BY ProductPart.ProductCode""")]

            if not temp_cache:
                return {}

            parts_cache = {}
            parts = {}
            current_code = temp_cache[0][0]
            for part_line in temp_cache:
                if current_code != part_line[0]:
                    parts_cache[current_code] = parts
                    current_code = part_line[0]
                    parts = {}

                parts[part_line[1]] = part_line[2]

            parts_cache[current_code] = parts
            return parts_cache
        finally:
            if conn:
                conn.close()

    def _product_prices_cache_renewer(self):
        conn = None
        try:
            all_prices = {}
            conn = persistence.Driver().open(self.mbcontext)
            all_prices["DL"] = Cache._query_all_prices_by_price_list(conn, "DL")
            all_prices["EI"] = Cache._query_all_prices_by_price_list(conn, "EI")
            return all_prices
        finally:
            if conn:
                conn.close()

    @staticmethod
    def _query_all_prices_by_price_list(conn, price_list):
        query_all_price_list = """
            SELECT productcode, 
                   context, 
                   defaultunitprice, 
                   addedunitprice, 
                   subtractedunitprice, 
                   pricelistid 
            FROM   price 
            WHERE  validthru >= Datetime(Datetime(), 'localtime') 
                   AND validfrom <= Datetime(Datetime(), 'localtime') 
                   AND pricelistid = '{}' """

        return {(str(x.get_entry(0)), str(x.get_entry(1) or '')):
                (x.get_entry(2) or '0.00', x.get_entry(3) or '0.00', x.get_entry(4) or 0)
                for x in conn.select(query_all_price_list.format(price_list))}

    def _price_key_cache_renewer(self):
        conn = None
        try:
            all_prices_key = {}
            conn = persistence.Driver().open(self.mbcontext)
            all_prices_key["DL"] = Cache._query_all_price_keys_by_price_list(conn, "DL")
            all_prices_key["EI"] = Cache._query_all_price_keys_by_price_list(conn, "EI")
            return all_prices_key
        finally:
            if conn:
                conn.close()

    @staticmethod
    def _query_all_price_keys_by_price_list(conn, price_list):
        query_all_price_keys_by_price_list = """
            SELECT productcode, 
                   context, 
                   pricekey, 
                   pricelistid 
            FROM   price 
            WHERE  validthru >= Datetime(Datetime(), 'localtime') 
                   AND validfrom <= Datetime(Datetime(), 'localtime') 
                   AND pricelistid = '{}' """

        return {(str(x.get_entry(0)), str(x.get_entry(1) or '')): x.get_entry(2)
                for x in conn.select(query_all_price_keys_by_price_list.format(price_list))}

    def _must_modify_cache_renewer(self):
        conn = None
        try:
            conn = persistence.Driver().open(self.mbcontext)
            return {str(x.get_entry(0)): str(x.get_entry(1)).split("=")[1] for x in conn.select(
                """SELECT ProductCode, Tag from ProductTags where Tag like 'MustBeModifiedSet%' """)}
        finally:
            if conn:
                conn.close()

    def _dt_only_cache_renewer(self):
        conn = None
        try:
            conn = persistence.Driver().open(self.mbcontext)
            return {str(x.get_entry(0)): str(x.get_entry(1)).split("=")[1] for x in
                    conn.select("""SELECT ProductCode, Tag from ProductTags where Tag like 'DTOnly%' """)}
        finally:
            if conn:
                conn.close()

    def _discount_cache_renewer(self):
        conn = None
        try:
            conn = persistence.Driver().open(self.mbcontext)
            return {(str(x.get_entry(0)), str(x.get_entry(1))): (x.get_entry(3), x.get_entry(4)) for x
                    in conn.select("""SELECT * from ProductDiscounts where Exclude == 'N'""")}
        finally:
            if conn:
                conn.close()

    def _options_cache_renewer(self):
        conn = None
        try:
            conn = persistence.Driver().open(self.mbcontext)
            query_result = [(str(x.get_entry(0)), str(x.get_entry(1)), str(x.get_entry(2)), str(x.get_entry(3)),
                             str(x.get_entry(4)), str(x.get_entry(5))) for x in conn.select("""
            select pc.ClassCode, p.ProductName, pt.Tag, pc.ProductCode, p2.ProductName, pt2.Tag from ProductClassification pc
            inner join Product p
            on pc.ClassCode = p.ProductCode
            left outer join ProductTags pt
            on p.ProductCode = pt.ProductCode
            inner join Product p2
            on p2.ProductCode = pc.ProductCode
            left outer join ProductTags pt2
            on p2.ProductCode = pt2.ProductCode
            where (pt.Tag like 'DisplayName%%' or pt.Tag like 'ItemQtys%%' or pt2.Tag like 'Color%%')
            and ClassCode <> 1
            order by pc.ClassCode, p.ProductCode""")]

            if not query_result:
                return

            new_option_cache = {}

            current_modifier_set = ModifierSet()
            current_modifier_set.part_code = query_result[0][0]
            current_modifier_set.product_name = query_result[0][1]
            current_modifier_set.default_qty = 1
            current_modifier_set.min_qty = 1
            current_modifier_set.max_qty = 1
            current_modifier_set.min_item_qty = 0
            current_modifier_set.max_item_qty = 1
            if query_result[0][2].upper().startswith("DISPLAYNAME"):
                current_modifier_set.display_name = query_result[0][2].split("=")[1]
                pass
            elif query_result[0][2].upper().startswith("ITEMQTYS"):
                item_qtys = query_result[0][2].split("=")[1]
                current_modifier_set.min_item_qty = item_qtys.split(";")[0]
                current_modifier_set.max_item_qty = item_qtys.split(";")[1]

            products_processed = {}
            modifiers = {}
            for query_line in query_result:
                if current_modifier_set.part_code != query_line[0]:
                    current_modifier_set.modifiers = modifiers
                    new_option_cache[current_modifier_set.part_code] = current_modifier_set

                    current_modifier_set = ModifierSet()
                    current_modifier_set.part_code = query_line[0]
                    current_modifier_set.product_name = query_line[1]
                    current_modifier_set.default_qty = 1
                    current_modifier_set.min_qty = 1
                    current_modifier_set.max_qty = 1
                    current_modifier_set.min_item_qty = 0
                    current_modifier_set.max_item_qty = 1
                    if query_line[2].upper().startswith("DISPLAYNAME"):
                        current_modifier_set.display_name = query_line[2].split("=")[1]
                        pass
                    elif query_line[2].upper().startswith("ITEMQTYS"):
                        item_qtys = query_line[2].split("=")[1]
                        current_modifier_set.min_item_qty = item_qtys.split(";")[0]
                        current_modifier_set.max_item_qty = item_qtys.split(";")[1]

                    modifiers = {}
                    products_processed = {}

                if query_line[2].upper().startswith("DISPLAYNAME"):
                    current_modifier_set.display_name = query_line[2].split("=")[1]
                    pass
                elif query_line[2].upper().startswith("ITEMQTYS"):
                    item_qtys = query_line[2].split("=")[1]
                    current_modifier_set.min_item_qty = item_qtys.split(";")[0]
                    current_modifier_set.max_item_qty = item_qtys.split(";")[1]

                if query_line[3] not in products_processed:
                    mod = Modifier()
                    mod.part_code = query_line[3]
                    mod.product_name = query_line[4]
                    if query_line[5].upper().startswith("COLOR"):
                        mod.color = query_line[5].split("=")[1]

                    modifiers[mod.part_code] = mod
                    products_processed[mod.part_code] = mod
                else:
                    if query_line[5].upper().startswith("COLOR"):
                        mod = products_processed[query_line[3]]
                        mod.color = query_line[5].split("=")[1]

            current_modifier_set.modifiers = modifiers
            new_option_cache[current_modifier_set.part_code] = current_modifier_set

            return new_option_cache
        finally:
            if conn:
                conn.close()

cache = Cache(pyscripts.mbcontext)
