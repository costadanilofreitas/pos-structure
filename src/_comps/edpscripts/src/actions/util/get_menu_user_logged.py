MENU_MANAGAR_AUTHENTICATED_USER = None

def get_menu_manager_authenticated_user():
    return MENU_MANAGAR_AUTHENTICATED_USER

def set_menu_manager_authenticated_user(user_id):
    global MENU_MANAGAR_AUTHENTICATED_USER
    MENU_MANAGAR_AUTHENTICATED_USER = user_id

