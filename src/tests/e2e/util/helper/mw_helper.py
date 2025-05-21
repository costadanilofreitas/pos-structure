# -*- coding: utf-8 -*-


def get_part_code_list(items):
    ret = []
    for item in items:
        if item.get('partCode'):
            ret.append(item['partCode'])
        [ret.append(x) for x in get_part_code_list(item.get('parts') or [])]
    return ret
