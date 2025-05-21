import sysactions


def get_customer_info_config(pos_id):
    document = sysactions.get_cfg(pos_id).find_values("CustomerInfoRequest/Document") or []
    name = sysactions.get_cfg(pos_id).find_values("CustomerInfoRequest/Name") or []

    return {'document': document, 'name': name}
