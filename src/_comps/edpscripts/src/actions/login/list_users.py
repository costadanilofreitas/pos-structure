# -*- coding: utf-8 -*-

import json

import sysactions


@sysactions.action
def get_user_list(pos_id, *args):
    user_xml_str = sysactions.get_user_information()
    return json.dumps(user_xml_str)
