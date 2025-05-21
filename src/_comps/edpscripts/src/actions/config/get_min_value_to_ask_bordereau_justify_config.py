def get_min_value_to_ask_bordereau_justify_config(config):
    return int(config.find_value("Customizations/MinValueToAskBordereauJustify") or 0)
