from json import JSONEncoder

from ._StaticConfig import StaticConfig


class StaticConfigJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, StaticConfig):
            return {
                "timeToAlertTableOpened": o.time_to_alert_table_opened,
                "timeToAlertTableIsIdle": o.time_to_alert_table_is_idle,
                "timeToAlertTableIsIdleWarning": o.time_to_alert_table_is_idle_warning,
                "timeToAlertRecallDeliveryIsIdle": o.time_to_alert_recall_delivery_is_idle,
                "recallButton": o.recall_button,
                "operatorButton": o.operator_button,
                "specialMenus": o.special_menus,
                "enabledTags": o.enabled_tags,
                "screenTimeout": o.screen_timeout,
                "cancelTimeoutWindow": o.cancel_timeout_window,
                "showInDashboard": o.show_in_dashboard,
                "productsScreenDimensions": o.products_screen_dimensions,
                "spinnerConfig": o.spinner_config,
                "enableTabBtns": o.enable_tab_btns,
                "enablePreStartSale": o.enable_pre_start_sale,
                "availableSaleTypes": o.available_sale_types,
                "fetchStoredOrdersTimeout": o.fetch_stored_orders_timeout,
                "tenderTypes": o.tender_types,
                "priceOverrideEnabled": o.price_override_enabled,
                "canOpenTableFromAnotherOperator": o.can_open_table_from_another_operator,
                "canEditOrder": o.can_edit_order,
                "satInfo": o.sat_info,
                "navigationOptions": o.navigation_config,
                "showCashInAndCashOut": o.show_cash_in_and_cash_out,
                "productionCourses": o.production_courses_dict,
                "minLevelNeededToSeeAllTables": o.min_level_needed_to_see_all_tables,
                "totemConfigurations": o.totem_config,
                "cashPaymentEnabled": o.cash_payment_enabled,
                "discountsEnabled": o.discounts_enabled,
                "billPaymentEnabled": o.bill_payment_enabled,
                "specialModifiers": o.special_modifiers,
                "showRupturedProducts": o.show_ruptured_products,
                "posNavigation": o.pos_navigation,
                "remoteOrderStatus": o.remote_order_status,
                "deliverySound": o.delivery_sound,
                'deliveryAddress': o.delivery_address
            }

        return super(StaticConfigJsonEncoder, self).default(o)
