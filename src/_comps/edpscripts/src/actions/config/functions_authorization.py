from systools import sys_log_error


def get_function_authorization_level_from_config(config, function_name):
    try:
        config_manager_authorization = config.find_value("Customizations/ManagerAuthorizationLevel/" + function_name)
        if config_manager_authorization is not None:
            return int(config_manager_authorization)
        return -1
    except Exception as _:
        sys_log_error("Erro getting table manager authorization")
        return -1
