# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\wrappers\python\ui.py
import pyscripts
import sysactions
import systools
import json
import persistence
from copy import deepcopy
mbcontext = pyscripts.mbcontext
_modifiers = None
_sub_modifiers = {}
_product_nav = {}
_dimensions = None

def get_cached_modifiers():
    global _modifiers
    global _sub_modifiers
    if _modifiers is None:
        _sub_modifiers = {}
        conn = persistence.Driver().open(mbcontext)
        modifiers = {}
        query = 'SELECT *\n                   FROM (\n                     SELECT\n                       P1.ProductCode AS productCode,\n                       P1.ProductName AS productName,\n                       P2.ProductCode AS modifierCode,\n                       P2.ProductName AS modifierName,\n                       COALESCE((SELECT 1 FROM productdb.ProductClassification WHERE ClassCode=P2.ProductCode LIMIT 1),0) AS isOption,\n                       (\n                         SELECT (\'[\' || COALESCE(GROUP_CONCAT(\'[\'||PC.ProductCode||\',"\'||PPC.ProductName||\'"]\'),\'\') || \']\')\n                         FROM ProductClassification PC\n                         JOIN Product PPC ON PPC.ProductCode=PC.ProductCode\n                         WHERE PC.ClassCode=P2.ProductCode\n                       ) AS options,\n                       ModifierType.CustomParamValue AS modifierType,\n                       ParentModifier.CustomParamValue AS parentModifierCode,\n                       PP.MinQty AS minQty,\n                       PP.MaxQty AS maxQty,\n                       PP.DefaultQty AS defaultQty,\n                       PP.IncludedQty AS includedQty,\n                       PP.Plain AS plain,\n                       PP.CustomAttr AS customAttr\n                     FROM productdb.ProductPart PP\n                     JOIN productdb.Product P1 ON P1.ProductCode=PP.ProductCode\n                     JOIN productdb.Product P2 ON P2.ProductCode=PP.PartCode\n                     LEFT JOIN productdb.ProductCustomParams ModifierType ON ModifierType.ProductCode=PP.PartCode AND ModifierType.CustomParamId=\'ModifierType\'\n                     LEFT JOIN productdb.ProductCustomParams ParentModifier ON ParentModifier.ProductCode=PP.PartCode AND ParentModifier.CustomParamId=\'ParentModifier\'\n                   ) T\n                   ORDER BY productCode, modifierCode'
        cursor = conn.select(query)
        if cursor.rows() > 0:
            for row in cursor:
                product_code, product_name, mod_code, mod_name, is_option, options, mod_type, parent_mod_code = map(row.get_entry, range(8))
                part_data = dict(zip(map(cursor.get_name, range(8, 14)), map(row.get_entry, range(8, 14))))
                if product_code not in modifiers:
                    modifiers[product_code] = {'name': product_name,
                     'parts': {}}
                if mod_code not in _sub_modifiers:
                    _sub_modifiers[str(mod_code)] = mod_name
                if int(is_option) > 0 and options is not None:
                    part_data['options'] = []
                    for pcode, pname in json.loads(options):
                        part_data['options'].append(int(pcode))
                        _sub_modifiers[str(pcode)] = pname

                if 'customAttr' in part_data:
                    try:
                        part_data['customAttr'] = json.loads(part_data['customAttr']) if part_data['customAttr'] is not None else None
                    except:
                        pass

                if mod_code not in modifiers[product_code]['parts']:
                    modifiers[product_code]['parts'][mod_code] = {'type': mod_type,
                     'isOption': int(is_option) > 0,
                     'parent': parent_mod_code,
                     'data': part_data}

        conn.close()
        _modifiers = modifiers
    return {'modifiers': _modifiers,
     'descriptions': _sub_modifiers}


@sysactions.action
def getModifiers(posid):
    return json.dumps(get_cached_modifiers())


def get_product_nav(max_levels = 4, default_descr_id = 1):
    """
    Retrieves UI product navigation info, as a JSON representing the four levels of navigation
    """
    global _product_nav
    if _product_nav:
        return _product_nav
    query_l1 = '\n        SELECT DISTINCT L1.Name, PN.ClassCode, L1.ButtonText\n    '
    for l in range(1, max_levels + 1):
        if l == 1:
            query_l1 += '\n            FROM Navigation L{0}\n            '.format(l)
        else:
            query_l1 += '\n            LEFT JOIN Navigation L{0} ON L{0}.ParentNavId=L{1}.NavId\n            '.format(l, l - 1)

    query_l1 += '\n        LEFT JOIN ProductNavigation PN ON PN.NavId IN ({0})\n        WHERE L1.ParentNavId IS NULL AND PN.ClassCode IN (\n            SELECT ProductCode\n            FROM ProductKernelParams PKP\n            WHERE PKP.ProductType=3\n        )\n    '.format(','.join([ 'L{0}.NavId'.format(l) for l in range(2, max_levels + 1) ]))
    slct = ', '.join([ 'Nav.L{0}Name, Nav.L{0}, Nav.L{0}Color'.format(sl) for sl in range(1, max_levels + 1) ])
    lvl_query = "\n      SELECT\n        {0},\n        COALESCE(GROUP_CONCAT(Nav.ClassCode, '|'),'') AS ClassCode,\n        P.ProductCode AS ProductCode,\n        COALESCE(PD.ProductDescription, P.ProductName, '') AS ButtonText\n    ".format(slct)
    lvl_query += '\n    FROM (\n        SELECT DISTINCT\n    '
    for l in range(1, max_levels + 1):
        if l == 1:
            lvl_query += '\n                 L{0}.Name AS L{0}Name,\n                 L{0}.ButtonText AS L{0},\n                 L{0}.NavId AS L{0}NavId,\n                 L{0}.ButtonColor AS L{0}Color,\n                 L{0}.SortOrder AS L{0}SortOrder,\n            '.format(l)
        elif l < max_levels:
            navids = ','.join([ 'L{0}.NavId'.format(sl) for sl in range(l, max_levels + 1) ])
            lvl_query += '\n                 CASE WHEN PN.NavId IN ({1}) THEN L{0}.Name ELSE NULL END AS L{0}Name,\n                 CASE WHEN PN.NavId IN ({1}) THEN L{0}.ButtonText ELSE NULL END AS L{0},\n                 CASE WHEN PN.NavId IN ({1}) THEN L{0}.NavId ELSE NULL END AS L{0}NavId,\n                 CASE WHEN PN.NavId IN ({1}) THEN L{0}.ButtonColor ELSE NULL END AS L{0}Color,\n                 CASE WHEN PN.NavId IN ({1}) THEN L{0}.SortOrder ELSE NULL END AS L{0}SortOrder,\n            '.format(l, navids)
        else:
            lvl_query += '\n                 CASE WHEN PN.NavId=L{0}.NavId THEN L{0}.Name ELSE NULL END AS L{0}Name,\n                 CASE WHEN PN.NavId=L{0}.NavId THEN L{0}.ButtonText ELSE NULL END AS L{0},\n                 CASE WHEN PN.NavId=L{0}.NavId THEN L{0}.NavId ELSE NULL END AS L{0}NavId,\n                 CASE WHEN PN.NavId=L{0}.NavId THEN L{0}.ButtonColor ELSE NULL END AS L{0}Color,\n                 CASE WHEN PN.NavId=L{0}.NavId THEN L{0}.SortOrder ELSE NULL END AS L{0}SortOrder,\n            '.format(l)

    lvl_query += '\n        PN.ProductCode AS ProductCode,\n        PN.ClassCode AS ClassCode\n    '
    for l in range(1, max_levels + 1):
        if l == 1:
            lvl_query += '\n              FROM Navigation L{0}\n            '.format(l)
        else:
            lvl_query += '\n              LEFT JOIN Navigation L{0} ON L{0}.ParentNavId=L{1}.NavId\n            '.format(l, l - 1)

    lvl_query += '\n        LEFT JOIN ProductNavigation PN ON PN.NavId IN ({0})\n    '.format(','.join([ 'L{0}.NavId'.format(l) for l in range(max_levels, 1, -1) ]))
    grp_by = ', '.join([ 'Nav.L{0}NavId'.format(sl) for sl in range(1, max_levels + 1) ])
    ord_by = ', '.join([ 'Nav.L{0}SortOrder'.format(sl) for sl in range(1, max_levels + 1) ])
    lvl_query += '\n      WHERE L1.ParentNavId IS NULL AND PN.ProductCode IS NOT NULL\n    ) Nav\n    JOIN Product P ON P.ProductCode=Nav.ProductCode\n    JOIN ProductKernelParams PKP ON PKP.ProductCode=P.ProductCode\n    LEFT JOIN ProductDescriptions PD ON PD.ProductCode=P.ProductCode AND PD.DescrId={0}\n    GROUP BY {1}, P.ProductCode\n    ORDER BY {2}, PKP.ProductPriority, COALESCE(PD.ProductDescription, P.ProductName)\n    '.format(default_descr_id, grp_by, ord_by)
    conn = persistence.Driver().open(mbcontext)
    L1_MENU = {'Menu': ('1', 'Menu')}
    cursor = conn.select(query_l1)
    if cursor.rows() > 0:
        L1_MENU = dict([ (r.get_entry(0), (r.get_entry(1), r.get_entry(2))) for r in cursor ])
    nav = {}
    for l1_name in L1_MENU.keys():
        l1_code, l1_desc = L1_MENU[l1_name]
        nav[l1_code] = {'name': l1_name,
         'text': l1_desc,
         'groups': []}

    def buildmax_levels(level_nav, product_cfg, level_cfg, level = 2, color = '#cccccc'):
        name, text, level_color = level_cfg['L{0}Name'.format(level)], level_cfg['L{0}'.format(level)], level_cfg['L{0}Color'.format(level)]
        has_next_level = 'L{0}Name'.format(level + 1) in level_cfg and level_cfg['L{0}Name'.format(level + 1)] is not None
        found = False
        for grp in level_nav['groups']:
            if grp['name'] == name:
                found = True
                break

        if not found:
            grp = {'name': name,
             'text': text,
             'groups': [],
             'items': [],
             'classes': []}
            level_nav['groups'].append(grp)
        if has_next_level:
            classes = buildmax_levels(grp, product_cfg, level_cfg, level + 1, level_color or color)
            classes.extend(grp['classes'])
            grp['classes'] = list(set(classes))
            return deepcopy(grp['classes'])
        else:
            item = {'text': product_cfg['ButtonText'],
             'classes': list(set(product_cfg['ClassCode'].split('|'))),
             'plu': product_cfg['ProductCode'],
             'bgColor': level_color or color}
            grp['items'].append(item)
            grp['classes'].extend(item['classes'])
            grp['classes'] = list(set(grp['classes']))
            return deepcopy(item['classes'])
            return

    cursor = conn.select(lvl_query)
    if cursor.rows() > 0:
        for row in cursor:
            n = dict(zip(map(cursor.get_name, range(3 * max_levels)), map(row.get_entry, range(3 * max_levels))))
            p = dict(zip(map(cursor.get_name, range(3 * max_levels, 3 * max_levels + 3)), map(row.get_entry, range(3 * max_levels, 3 * max_levels + 3))))
            if n.get('L1Name', '') not in L1_MENU:
                systools.sys_log_warning("Invalid L1 menu '{0}' for PLU {1}".format(n.get('L1Name', ''), n.get('ProductCode', '')))
                continue
            l1_code, _ = L1_MENU[n['L1Name']]
            buildmax_levels(nav[l1_code], p, n)

    conn.close()
    _product_nav = nav
    return _product_nav


@sysactions.action
def getNavigationData(posid, max_levels = 4, default_descr_id = 1):
    return json.dumps(get_product_nav(max_levels, default_descr_id))


def get_dimensions():
    global _dimensions
    if _dimensions is None:
        data = {}
        query = 'SELECT DimChar, DimDescr FROM Dimensions'
        conn = persistence.Driver().open(mbcontext)
        cursor = conn.select(query)
        desc = {}
        if cursor.rows() > 0:
            desc = dict([ (row.get_entry(0), row.get_entry(1)) for row in cursor ])
        data['desc'] = desc
        query = 'SELECT DimGroupId, DimChar, ProductCode FROM DimensionGroups'
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

        data['groups'] = groups
        data['plu'] = plu
        conn.close()
        _dimensions = data
    return _dimensions


@sysactions.action
def getDimensions(posid):
    return json.dumps(get_dimensions())


@sysactions.action
def doAuthorize(posid, min_level = None, timeout = 60000):
    model = sysactions.get_model(posid)
    return sysactions.get_authorization(posid, min_level=min_level, model=model, timeout=timeout)


@sysactions.action
def selectTheme(posid, options, *args):
    options = options.split('|')
    model = sysactions.get_model(posid)
    current = sysactions.get_custom(model, 'THEME', 'default')
    index = sysactions.show_listbox(posid, options, defvalue=options.index(current) if current in options else None)
    if index is None:
        return
    else:
        sysactions.set_custom(posid, 'THEME', options[index], persist=True)
        return options[index]