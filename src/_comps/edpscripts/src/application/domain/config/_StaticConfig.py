
class StaticConfig(object):
    def __init__(self,
                 time_to_alert_table_opened,
                 time_to_alert_table_is_idle,
                 time_to_alert_table_is_idle_warning,
                 time_to_alert_recall_delivery_is_idle,
                 recall_button,
                 operator_button,
                 special_menus,
                 enabled_tags,
                 screen_timeout,
                 cancel_timeout_window,
                 show_in_dashboard,
                 products_screen_dimensions,
                 spinner_config,
                 enable_tab_btns,
                 enable_pre_start_sale,
                 available_sale_types,
                 fetch_stored_orders_timeout,
                 tender_types,
                 price_override_enabled,
                 can_open_table_from_another_operator,
                 can_edit_order,
                 sat_info,
                 navigation_config,
                 show_cash_in_and_cash_out,
                 production_courses_dict,
                 min_level_needed_to_see_all_tables,
                 totem_config,
                 cash_payment_enabled,
                 discounts_enabled,
                 bill_payment_enabled,
                 special_modifiers,
                 show_ruptured_products,
                 pos_navigation,
                 remote_order_status,
                 delivery_sound,
                 delivery_address):
        self.time_to_alert_table_opened = time_to_alert_table_opened
        self.time_to_alert_table_is_idle = time_to_alert_table_is_idle
        self.time_to_alert_table_is_idle_warning = time_to_alert_table_is_idle_warning
        self.time_to_alert_recall_delivery_is_idle = time_to_alert_recall_delivery_is_idle
        self.recall_button = recall_button
        self.operator_button = operator_button
        self.special_menus = special_menus
        self.enabled_tags = enabled_tags
        self.screen_timeout = screen_timeout
        self.cancel_timeout_window = cancel_timeout_window
        self.show_in_dashboard = show_in_dashboard
        self.products_screen_dimensions = products_screen_dimensions
        self.spinner_config = spinner_config
        self.enable_tab_btns = enable_tab_btns
        self.enable_pre_start_sale = enable_pre_start_sale
        self.available_sale_types = available_sale_types
        self.fetch_stored_orders_timeout = fetch_stored_orders_timeout
        self.tender_types = tender_types
        self.price_override_enabled = price_override_enabled
        self.can_open_table_from_another_operator = can_open_table_from_another_operator
        self.can_edit_order = can_edit_order
        self.sat_info = sat_info
        self.navigation_config = navigation_config
        self.show_cash_in_and_cash_out = show_cash_in_and_cash_out
        self.production_courses_dict = production_courses_dict
        self.min_level_needed_to_see_all_tables = min_level_needed_to_see_all_tables
        self.totem_config = totem_config
        self.cash_payment_enabled = cash_payment_enabled
        self.discounts_enabled = discounts_enabled
        self.bill_payment_enabled = bill_payment_enabled
        self.special_modifiers = special_modifiers
        self.show_ruptured_products = show_ruptured_products
        self.pos_navigation = pos_navigation
        self.remote_order_status = remote_order_status
        self.delivery_sound = delivery_sound
        self.delivery_address = delivery_address
