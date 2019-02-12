from pyscriptscache import ModifierSets, Modifier, Part, cache as _cache


def get_modifiers_and_elements(modifier_sets, modifier_elem, modifier_part, context, part_code, level, pod_type):
    # type: (dict, dict, dict, str, str, int, str) -> None

    # Options - Pai tem default_qty = 1 e Filhos default_qty = 0
    # Ingredients - Pai tem default_qty = 0 e Filhos default_qty = 1
    all_options_tags = [_cache.get_tags_as_dict(part_code, "HasOptions"), _cache.get_tags_as_dict(part_code, "Ingredients")]

    options = []
    for options_tag in all_options_tags:
        if options_tag:
            options.extend(x.split(">")[0] for x in options_tag.split("|"))

    defaults = {}
    options_tag = all_options_tags[1]
    if len(options_tag.split(">")) > 1 and options_tag.split(">")[1]:
        defaults[options_tag.split(">")[0]] = [x for x in options_tag.split('|')[0].split(">")[1].split(";")]

    # Busca os valores Default, Min e Max de cada Option ou Ingredients
    qty_option = {x.split(">")[0]: x.split(">")[1].split(";") for x in _cache.get_tags_as_dict(part_code, "QtyOptions").split("|") if x != ""}

    # Busca quais options devem estar apenas no OrderTaker
    dt_only_list = _cache.get_tags_as_dict(part_code, "DTOnly").split("|")
    dt_only_dict = {}
    for dt_only in dt_only_list:
        dt_only_dict[dt_only] = dt_only

    if options:
        temp_modifiers_sets = ModifierSets()
        temp_modifiers_sets.context = context + '.' + part_code
        temp_modifiers_sets.level = level

        has_option = False
        for opt in options:
            if pod_type != "DT" and opt in dt_only_dict:
                continue
            has_option = True

            # OPTION - Code
            item_id = context + '.' + part_code
            temp_mod_set = _cache.get_options(opt)

            if opt in qty_option:
                temp_mod_set.default_qty = qty_option[opt][0]
                temp_mod_set.min_qty = qty_option[opt][1]
                temp_mod_set.max_qty = qty_option[opt][2]
            temp_modifiers_sets.modifiers_sets[opt] = temp_mod_set

            for mod_elem in temp_mod_set.modifiers:  # type: Modifier
                temp_elem = temp_mod_set.modifiers[mod_elem]
                temp_elem.context = item_id + "." + temp_mod_set.part_code

                # Set Default Qty for Ingredients
                if opt in defaults:
                    if mod_elem in defaults[opt]:
                        temp_elem.def_qty = 1
                        temp_elem.ord_qty = 1

                modifier_elem[temp_elem.context + "." + temp_elem.part_code] = temp_elem
                temp_elem.unit_price, temp_elem.add_price, temp_elem.sub_price = _cache.get_best_price(temp_elem.context, temp_elem.part_code, pod_type) or (0, 0, 0)

                # Go to the NEXT LEVEL AND BEYOND
                get_modifiers_and_elements(modifier_sets, modifier_elem, modifier_part, temp_elem.context, temp_elem.part_code, level + 1, pod_type)

        if has_option:
            modifier_sets[temp_modifiers_sets.context] = temp_modifiers_sets

    parts = _cache.get_parts(part_code)
    if parts:
        item_id = context + '.' + part_code
        modifier_part[item_id] = {}

        for part in parts:
            mod_part = Part()
            mod_part.unit_price, mod_part.add_price, mod_part.sub_price = _cache.get_best_price(item_id, part, pod_type) or (0, 0, 0)
            mod_part.part_code = part
            mod_part.context = item_id
            mod_part.def_qty, mod_part.min_qty, mod_part.max_qty, mod_part.product_name = parts[part]

            modifier_part[item_id][part] = mod_part

            # Go to the NEXT LEVEL
            get_modifiers_and_elements(modifier_sets, modifier_elem, modifier_part, item_id, part, level + 1, pod_type)
# END of insert_options_and_defaults
