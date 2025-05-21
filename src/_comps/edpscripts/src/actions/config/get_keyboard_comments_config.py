def get_keyboard_comments_config(config):
    config_comments = []
    if config.find_group("Customizations.KeyboardComments") is not None:
        config_comments = config.find_group("Customizations.KeyboardComments").keys or []
    comments = {}

    for key in config_comments:
        comments[key.name] = key.values

    return comments
