def find_key_value(view_group, key_name, default_value=""):
    key = [x for x in view_group.keys if x.name == key_name]

    return str(default_value) if not key else str(key[0].values[0])


def find_key_values(view_group, key_name):
    key = [x for x in view_group.keys if x.name == key_name]

    return [] if not key else key[0].values
