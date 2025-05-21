import json

import persistence
import pyscripts
import sysactions

mb_context = pyscripts.mbcontext
_modifiers = None
_sub_modifiers = {}


@sysactions.action
def get_modifiers_data(_):
    return json.dumps(get_cached_modifiers())


def get_cached_modifiers():
    global _modifiers
    global _sub_modifiers

    if _modifiers is None:
        _sub_modifiers = {}
        conn = persistence.Driver().open(mb_context)
        modifiers = {}
        query = """
        SELECT *
        FROM (
                SELECT 
                    P1.ProductCode AS productCode,
                    P1.ProductName AS productName,
                    P2.ProductCode AS modifierCode,
                    P2.ProductName AS modifierName,
                    COALESCE((SELECT 1 FROM productdb.ProductClassification WHERE ClassCode=P2.ProductCode LIMIT 1),0) AS isOption,
                    COALESCE((SELECT 1 FROM ProductKernelParams WHERE ProductCode=P2.ProductCode AND ProductType = 2 LIMIT 1),0) AS isCombo,
                    (SELECT ( '[ ' || COALESCE(GROUP_CONCAT( '[ '||PC.ProductCode|| '," '||PPC.ProductName|| '"] '), ' ') ||  '] ')  FROM ProductClassification PC  JOIN Product PPC ON PPC.ProductCode=PC.ProductCode  WHERE PC.ClassCode=P2.ProductCode) AS options,
                    ModifierType.CustomParamValue AS modifierType,
                    ParentModifier.CustomParamValue AS parentModifierCode,
                    PP.MinQty AS minQty,
                    PP.MaxQty AS maxQty,
                    PP.DefaultQty AS defaultQty,
                    PP.IncludedQty AS includedQty,
                    PP.Plain AS plain,PP.CustomAttr AS customAttr
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
                product_code, product_name, mod_code, mod_name, is_option, is_combo, options, mod_type, parent_mod_code = map(row.get_entry, range(9))
                part_data = dict(zip(map(cursor.get_name, range(9, 16)), map(row.get_entry, range(9, 16))))
                if product_code not in modifiers:
                    modifiers[product_code] = {'name': product_name, 'parts': {}}
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
                    modifiers[product_code]['parts'][mod_code] = {
                        'type': mod_type,
                        'isOption': int(is_option) > 0,
                        'isCombo': int(is_combo) > 0,
                        'parent': parent_mod_code,
                        'data': part_data
                    }

        conn.close()
        _modifiers = modifiers

    return {'modifiers': _modifiers, 'descriptions': _sub_modifiers}
