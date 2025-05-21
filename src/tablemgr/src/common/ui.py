import pyscripts
import sysactions
import systools
import json
import persistence
from copy import deepcopy


mbcontext = pyscripts.mbcontext


# Modifier's cache
_modifiers = None
_sub_modifiers = {}


# UI product navigation levels
_product_nav = {}


# Dimension's cache
_dimensions = None


def get_cached_modifiers():
    global _modifiers, _sub_modifiers

    if _modifiers is None:
        _sub_modifiers = {}
        conn = persistence.Driver().open(mbcontext)
        modifiers = {}
        query = """SELECT *
                   FROM (
                     SELECT
                       P1.ProductCode AS productCode,
                       P1.ProductName AS productName,
                       P2.ProductCode AS modifierCode,
                       P2.ProductName AS modifierName,
                       COALESCE((SELECT 1 FROM productdb.ProductClassification WHERE ClassCode=P2.ProductCode LIMIT 1),0) AS isOption,
                       (
                         SELECT ('[' || COALESCE(GROUP_CONCAT('['||PC.ProductCode||',"'||PPC.ProductName||'"]'),'') || ']')
                         FROM ProductClassification PC
                         JOIN Product PPC ON PPC.ProductCode=PC.ProductCode
                         WHERE PC.ClassCode=P2.ProductCode
                       ) AS options,
                       ModifierType.CustomParamValue AS modifierType,
                       ParentModifier.CustomParamValue AS parentModifierCode,
                       PP.MinQty AS minQty,
                       PP.MaxQty AS maxQty,
                       PP.DefaultQty AS defaultQty,
                       PP.IncludedQty AS includedQty,
                       PP.Plain AS plain,
                       PP.CustomAttr AS customAttr
                     FROM productdb.ProductPart PP
                     JOIN productdb.Product P1 ON P1.ProductCode=PP.ProductCode
                     JOIN productdb.Product P2 ON P2.ProductCode=PP.PartCode
                     LEFT JOIN productdb.ProductCustomParams ModifierType ON ModifierType.ProductCode=PP.PartCode AND ModifierType.CustomParamId='ModifierType'
                     LEFT JOIN productdb.ProductCustomParams ParentModifier ON ParentModifier.ProductCode=PP.PartCode AND ParentModifier.CustomParamId='ParentModifier'
                   ) T
                   ORDER BY productCode, modifierCode"""
        cursor = conn.select(query)
        if cursor.rows() > 0:
            for row in cursor:
                product_code, product_name, mod_code, mod_name, is_option, options, mod_type, parent_mod_code = map(row.get_entry, range(8))
                part_data = dict(zip(map(cursor.get_name, range(8, 14)), map(row.get_entry, range(8, 14))))
                if product_code not in modifiers:
                    modifiers[product_code] = {
                        "name": product_name,
                        "parts": {}
                    }
                if mod_code not in _sub_modifiers:
                    _sub_modifiers[str(mod_code)] = mod_name
                if int(is_option) > 0 and options is not None:
                    part_data["options"] = []
                    for pcode, pname in json.loads(options):
                        part_data["options"].append(int(pcode))
                        _sub_modifiers[str(pcode)] = pname
                if "customAttr" in part_data:
                    try:
                        part_data["customAttr"] = json.loads(part_data["customAttr"]) if part_data["customAttr"] is not None else None
                    except:
                        pass
                if mod_code not in modifiers[product_code]["parts"]:
                    modifiers[product_code]["parts"][mod_code] = {
                        "type": mod_type,
                        "isOption": (int(is_option) > 0),
                        "parent": parent_mod_code,
                        "data": part_data
                    }
        conn.close()
        _modifiers = modifiers

    return {"modifiers": _modifiers, "descriptions": _sub_modifiers}


@sysactions.action
def getModifiers(posid):
    return json.dumps(get_cached_modifiers())


def get_product_nav(max_levels=4, default_descr_id=1):
    """
    Retrieves UI product navigation info, as a JSON representing the four levels of navigation
    """
    #  Sample response
    #     {
    #         "1": {
    #             "text": "Retail",
    #             "groups": [
    #                 {
    #                     "classes": ["1"],
    #                     "text": "Main",
    #                     "groups": [
    #                         {
    #                             "classes": ["1"],
    #                             "text": "Appetisers",
    #                             "items": [
    #                                 {
    #                                     "text": "Houmous",
    #                                     "plu": 1000,
    #                                     "bgColor": "#dbc8db",
    #                                     "classes": ["1"]
    #                                 },
    #                                 {
    #                                     "text": "Hotpot",
    #                                     "plu": 1001,
    #                                     "bgColor": "#dbc8db",
    #                                     "classes": ["1"]
    #                                 },
    #                                 {
    #                                     "text": "Chiken Strips & Spicy Rice",
    #                                     "plu": 1002,
    #                                     "bgColor": "#dbc8db",
    #                                     "classes": ["1"]
    #                                 },
    #                                 {
    #                                     "text": "Chiken Strips, Veg & Spicy Rice",
    #                                     "plu": 1003,
    #                                     "bgColor": "#dbc8db",
    #                                     "classes": ["1"]
    #                                 },
    #                                 {
    #                                     "text": "6 Winglets & Single Chips",
    #                                     "plu": 1004,
    #                                     "bgColor": "#dbc8db",
    #                                     "classes": ["1"]
    #                                 },
    #                                 {
    #                                     "text": "Livers",
    #                                     "plu": 1005,
    #                                     "bgColor": "#dbc8db",
    #                                     "classes": ["1"]
    #                                 },
    #                                 {
    #                                     "text": "Giblets",
    #                                     "plu": 1006,
    #                                     "bgColor": "#dbc8db",
    #                                     "classes": ["1"]
    #                                 },
    #                             ],
    #                         },
    #                         {
    #                             "classes": ["1"],
    #                             "text": "Chicken",
    #                             "items": [
    #                                 {
    #                                     "text": "1/4 Chicken",
    #                                     "plu": 2000,
    #                                     "bgColor": "#dbc8db",
    #                                     "classes": ["1"]
    #                                 },
    #                                 {
    #                                     "text": "1/2 Chicken",
    #                                     "plu": 2001,
    #                                     "bgColor": "#dbc8db",
    #                                     "classes": ["1"]
    #                                 },
    #                                 {
    #                                     "text": "Full Chicken",
    #                                     "plu": 2002,
    #                                     "bgColor": "#dbc8db",
    #                                     "classes": ["1"]
    #                                 },
    #                                 {
    #                                     "text": "10 Winglets",
    #                                     "plu": 2003,
    #                                     "bgColor": "#dbc8db",
    #                                     "classes": ["1"]
    #                                 },
    #                                 {
    #                                     "text": "Chicken Espetada",
    #                                     "plu": 2004,
    #                                     "bgColor": "#dbc8db",
    #                                     "classes": ["1"]
    #                                 },
    #                                 {
    #                                     "text": "Grande Meal",
    #                                     "plu": 2005,
    #                                     "bgColor": "#dbc8db",
    #                                     "classes": ["1"]
    #                                 },
    #                             ],
    #                         }
    #                     ]
    #                 },
    #                 {
    #                     "classes": ["1"],
    #                     "text": "Sides",
    #                     "groups": []
    #                 },
    #                 {
    #                     "classes": ["1"],
    #                     "text": "Drinks & Desserts",
    #                     "groups": []
    #                 },
    #                 {
    #                     "classes": ["1"],
    #                     "text": "Beers",
    #                     "groups": []
    #                 },
    #                 {
    #                     "classes": ["1"],
    #                     "text": "Wines",
    #                     "groups": []
    #                 },
    #                 {
    #                     "classes": ["1"],
    #                     "text": "Catering",
    #                     "groups": []
    #                 },
    #                 {
    #                     "classes": ["1"],
    #                     "text": "Retail",
    #                     "groups": []
    #                 },
    #             ]
    #         }
    #     }
    global _product_nav

    if _product_nav:
        return _product_nav

    query_l1 = """
        SELECT DISTINCT L1.Name, PN.ClassCode, L1.ButtonText
    """
    for l in range(1, max_levels + 1):
        if l == 1:
            query_l1 += """
            FROM Navigation L{0}
            """.format(l)
        else:
            query_l1 += """
            LEFT JOIN Navigation L{0} ON L{0}.ParentNavId=L{1}.NavId
            """.format(l, l - 1)
    query_l1 += """
        LEFT JOIN ProductNavigation PN ON PN.NavId IN ({0})
        WHERE L1.ParentNavId IS NULL AND PN.ClassCode IN (
            SELECT ProductCode
            FROM ProductKernelParams PKP
            WHERE PKP.ProductType=3
        )
    """.format(",".join(["L{0}.NavId".format(l) for l in range(2, max_levels + 1)]))

    slct = ", ".join(["Nav.L{0}Name, Nav.L{0}, Nav.L{0}Color".format(sl) for sl in range(1, max_levels + 1)])
    lvl_query = """
      SELECT
        {0},
        COALESCE(GROUP_CONCAT(Nav.ClassCode, '|'),'') AS ClassCode,
        P.ProductCode AS ProductCode,
        COALESCE(PD.ProductDescription, P.ProductName, '') AS ButtonText
    """.format(slct)
    lvl_query += """
    FROM (
        SELECT DISTINCT
    """
    for l in range(1, max_levels + 1):
        if l == 1:
            lvl_query += """
                 L{0}.Name AS L{0}Name,
                 L{0}.ButtonText AS L{0},
                 L{0}.NavId AS L{0}NavId,
                 L{0}.ButtonColor AS L{0}Color,
                 L{0}.SortOrder AS L{0}SortOrder,
            """.format(l)
        elif l < max_levels:
            navids = ",".join(["L{0}.NavId".format(sl) for sl in range(l, max_levels + 1)])
            lvl_query += """
                 CASE WHEN PN.NavId IN ({1}) THEN L{0}.Name ELSE NULL END AS L{0}Name,
                 CASE WHEN PN.NavId IN ({1}) THEN L{0}.ButtonText ELSE NULL END AS L{0},
                 CASE WHEN PN.NavId IN ({1}) THEN L{0}.NavId ELSE NULL END AS L{0}NavId,
                 CASE WHEN PN.NavId IN ({1}) THEN L{0}.ButtonColor ELSE NULL END AS L{0}Color,
                 CASE WHEN PN.NavId IN ({1}) THEN L{0}.SortOrder ELSE NULL END AS L{0}SortOrder,
            """.format(l, navids)
        else:
            lvl_query += """
                 CASE WHEN PN.NavId=L{0}.NavId THEN L{0}.Name ELSE NULL END AS L{0}Name,
                 CASE WHEN PN.NavId=L{0}.NavId THEN L{0}.ButtonText ELSE NULL END AS L{0},
                 CASE WHEN PN.NavId=L{0}.NavId THEN L{0}.NavId ELSE NULL END AS L{0}NavId,
                 CASE WHEN PN.NavId=L{0}.NavId THEN L{0}.ButtonColor ELSE NULL END AS L{0}Color,
                 CASE WHEN PN.NavId=L{0}.NavId THEN L{0}.SortOrder ELSE NULL END AS L{0}SortOrder,
            """.format(l)
    lvl_query += """
        PN.ProductCode AS ProductCode,
        PN.ClassCode AS ClassCode
    """
    for l in range(1, max_levels + 1):
        if l == 1:
            lvl_query += """
              FROM Navigation L{0}
            """.format(l)
        else:
            lvl_query += """
              LEFT JOIN Navigation L{0} ON L{0}.ParentNavId=L{1}.NavId
            """.format(l, l - 1)
    lvl_query += """
        LEFT JOIN ProductNavigation PN ON PN.NavId IN ({0})
    """.format(",".join(["L{0}.NavId".format(l) for l in range(max_levels, 1, -1)]))
    grp_by = ", ".join(["Nav.L{0}NavId".format(sl) for sl in range(1, max_levels + 1)])
    ord_by = ", ".join(["Nav.L{0}SortOrder".format(sl) for sl in range(1, max_levels + 1)])
    lvl_query += """
      WHERE L1.ParentNavId IS NULL AND PN.ProductCode IS NOT NULL
    ) Nav
    JOIN Product P ON P.ProductCode=Nav.ProductCode
    JOIN ProductKernelParams PKP ON PKP.ProductCode=P.ProductCode
    LEFT JOIN ProductDescriptions PD ON PD.ProductCode=P.ProductCode AND PD.DescrId={0}
    GROUP BY {1}, P.ProductCode
    ORDER BY {2}, PKP.ProductPriority, COALESCE(PD.ProductDescription, P.ProductName)
    """.format(default_descr_id, grp_by, ord_by)

    conn = persistence.Driver().open(mbcontext)

    L1_MENU = {
        "Menu": ("1", "Menu")
    }

    cursor = conn.select(query_l1)
    if cursor.rows() > 0:
        L1_MENU = dict([(r.get_entry(0), (r.get_entry(1), r.get_entry(2))) for r in cursor])

    nav = {}
    for l1_name in L1_MENU.keys():
        l1_code, l1_desc = L1_MENU[l1_name]
        nav[l1_code] = {
            "name": l1_name,
            "text": l1_desc,
            "groups": []
        }

    def buildmax_levels(level_nav, product_cfg, level_cfg, level=2, color="#cccccc"):
        name, text, level_color = (level_cfg["L{0}Name".format(level)], level_cfg["L{0}".format(level)], level_cfg["L{0}Color".format(level)])
        has_next_level = (("L{0}Name".format(level + 1) in level_cfg) and (level_cfg["L{0}Name".format(level + 1)] is not None))
        found = False
        for grp in level_nav["groups"]:
            if grp["name"] == name:
                found = True
                break
        if not found:
            grp = {
                "name": name,
                "text": text,
                "groups": [],
                "items": [],
                "classes": []
            }
            level_nav["groups"].append(grp)
        if has_next_level:
            classes = buildmax_levels(grp, product_cfg, level_cfg, level + 1, (level_color or color))
            classes.extend(grp["classes"])
            grp["classes"] = list(set(classes))
            return deepcopy(grp["classes"])
        else:
            item = {
                "text": product_cfg["ButtonText"],
                "classes": list(set(product_cfg["ClassCode"].split("|"))),
                "plu": product_cfg["ProductCode"],
                "bgColor": (level_color or color)
            }
            grp["items"].append(item)
            grp["classes"].extend(item["classes"])
            grp["classes"] = list(set(grp["classes"]))
            return deepcopy(item["classes"])

    cursor = conn.select(lvl_query)
    if cursor.rows() > 0:
        for row in cursor:
            # get navigation levels information
            n = dict(zip(map(cursor.get_name, range((3 * max_levels))), map(row.get_entry, range(3 * max_levels))))
            # get product information
            p = dict(zip(map(cursor.get_name, range((3 * max_levels), (3 * max_levels) + 3)), map(row.get_entry, range((3 * max_levels), (3 * max_levels) + 3))))
            # sanity check
            if n.get("L1Name", "") not in L1_MENU:
                systools.sys_log_warning("Invalid L1 menu '{0}' for PLU {1}".format(n.get("L1Name", ""), n.get("ProductCode", "")))
                continue
            # level 1 navigation pointer
            l1_code, _ = L1_MENU[n["L1Name"]]
            # build rest of levels
            buildmax_levels(nav[l1_code], p, n)
    conn.close()
    _product_nav = nav
    return _product_nav


@sysactions.action
def getNavigationData(posid, max_levels=4, default_descr_id=1):
    return json.dumps(get_product_nav(max_levels, default_descr_id))


def get_dimensions():
    global _dimensions
    if _dimensions is None:
        data = {}
        # dimensions available and their descriptions
        query = """SELECT DimChar, DimDescr FROM Dimensions"""
        conn = persistence.Driver().open(mbcontext)
        cursor = conn.select(query)
        desc = {}
        if cursor.rows() > 0:
            desc = dict([(row.get_entry(0), row.get_entry(1)) for row in cursor])
        data["desc"] = desc
        # now retrieve product dimensions
        query = """SELECT DimGroupId, DimChar, ProductCode FROM DimensionGroups"""
        cursor = conn.select(query)
        groups = {}
        plu = {}
        if cursor.rows() > 0:
            for row in cursor:
                group_id, dim, pcode = map(row.get_entry, range(3))
                group_id = int(group_id)
                if group_id not in groups:
                    groups[group_id] = {}
                groups[group_id][dim] = pcode
                plu[pcode] = group_id
        data["groups"] = groups
        data["plu"] = plu
        conn.close()
        _dimensions = data
    return _dimensions


@sysactions.action
def getDimensions(posid):
    return json.dumps(get_dimensions())


@sysactions.action
def doAuthorize(posid, min_level=None, timeout=60000):
    model = sysactions.get_model(posid)
    return sysactions.get_authorization(posid, min_level=min_level, model=model, timeout=timeout)


@sysactions.action
def selectTheme(posid, options, *args):
    options = options.split("|")
    model = sysactions.get_model(posid)
    current = sysactions.get_custom(model, "THEME", "default")
    index = sysactions.show_listbox(posid, options, defvalue=options.index(current) if current in options else None)
    if index is None:
        return  # User cancelled
    sysactions.set_custom(posid, "THEME", options[index], persist=True)
    return options[index]
