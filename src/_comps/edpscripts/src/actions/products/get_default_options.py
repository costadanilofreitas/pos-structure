import persistence
import json
from systools import sys_log_exception
from sysactions import action

from .. import mb_context
_default_options = None


def _get_default_options(pos_id='1'):
    global _default_options
    if _default_options is None:
        query = """select ProductCode as Product, CustomParamValue as Defaultoptions from ProductCustomParams pcp where pcp.customparamid = 'defaultoption'"""
        optionslist = {}
        try:
            conn = persistence.Driver().open(mb_context, pos_id)
            cursor = conn.select(query)
            for row in cursor:
                plu, options = map(row.get_entry, ("Product", "Defaultoptions"))
                product = {
                    "defaultParts": options.split('|')
                }
                optionslist[int(plu)] = product
        except:
            sys_log_exception("Error getting default option list")
        finally:
            if conn:
                conn.close()
        _default_options = optionslist

    return _default_options


@action
def getDefaultOptions(pos_id, *args):
    return json.dumps(_get_default_options(pos_id))
