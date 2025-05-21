# -*- coding: utf-8 -*-
import json
import sysactions

from typing import List

from actions import mb_context
from mw_helper import BaseRepository
from persistence import Connection

from ..models import Navigation, NavigationProduct


@sysactions.action
def get_navigation_data(_):
    navigations = _get_navigations()
    navigation_products = _get_navigation_products()
    navigations = populate_navigation_products(navigations, navigation_products)

    return json.dumps(navigations, default=lambda o: getattr(o, '__dict__', str(o)))


def _get_navigations():
    navigation_list = _get_navigation_list()
    main_navigations = _get_main_navigations(navigation_list)
    navigation_menus = _get_navigation_menus(main_navigations, navigation_list)

    return navigation_menus


def populate_navigation_products(navigations, navigation_products):
    # type: (List[Navigation], List[NavigationProduct]) -> List[Navigation]
    if len(navigation_products) == 0:
        return []

    for nav_menu in navigations:
        nav_menu_id = nav_menu.nav_id
        nav_menu.items.extend([prod for prod in navigation_products if prod.nav_id == nav_menu_id])
        navigation_products = [prod for prod in navigation_products if prod.nav_id != nav_menu_id]
        populate_navigation_products(nav_menu.groups, navigation_products)

    return navigations


def _get_navigation_menus(navigation_menus, navigation_list):
    # type: (List[Navigation], List[Navigation]) -> List[Navigation]
    if len(navigation_list) == 0:
        return []

    for nav_menu in navigation_menus:
        navigation_child = _get_navigations_child(nav_menu, navigation_list)
        nav_menu.groups.extend(navigation_child)
        nav_with_parents = [nav.nav_id for nav in navigation_child]
        navigation_list = [nav for nav in navigation_list if nav.nav_id not in nav_with_parents]
        _get_navigation_menus(nav_menu.groups, navigation_list)

    return navigation_menus


def _get_navigations_child(nav_menu, navigation_list):
    # type: (Navigation, List[Navigation]) -> List[Navigation]
    nav_menu_id = nav_menu.nav_id
    nav_child = [nav for nav in navigation_list if nav.parent_nav_id == nav_menu_id]

    return nav_child


def _get_main_navigations(navigation_list):
    # type: (List[Navigation]) -> List[Navigation]
    navigation_menus = []
    for nav in navigation_list:
        if not nav.parent_nav_id:
            navigation_menus.append(nav)

    for nav in navigation_menus:
        navigation_list.remove(nav)

    return navigation_menus


def _get_navigation_list():
    # type: () -> List[Navigation]

    def inner_func(conn):
        # type: (Connection) -> List[Navigation]
        query = """
                    SELECT 
                       NavId, 
                       Name, 
                       ParentNavId, 
                       SortOrder, 
                       ButtonText, 
                       COALESCE(ButtonColor, '#CCCCCC') AS ButtonColor
                   FROM Navigation
                   ORDER BY SortOrder
               """

        res = list()
        for row in conn.select(query):
            nav = Navigation(nav_id=row.get_entry("NavId"),
                             name=row.get_entry("Name"),
                             parent_nav_id=row.get_entry("ParentNavId"),
                             sort_order=row.get_entry("SortOrder"),
                             button_text=row.get_entry("ButtonText"),
                             background_color=row.get_entry("ButtonColor"))
            res.append(nav)

        return res

    return BaseRepository(mb_context).execute_with_connection(inner_func)


def _get_navigation_products():
    # type: () -> List[NavigationProduct]
    def inner_func(conn):
        # type: (Connection) -> List[NavigationProduct]
        query = """
                   SELECT PN.NavId, 
                          PN.ClassCode, 
                          PN.ProductCode, 
                          P.ProductName, 
                          COALESCE(N.ButtonColor, '#CCCCCC') AS ButtonColor
                   FROM ProductNavigation PN
                   INNER JOIN Product P ON PN.ProductCode = P.ProductCode
                   LEFT JOIN Navigation N ON PN.NavId = N.NavId
                   JOIN ProductKernelParams PKP ON P.ProductCode = PKP.ProductCode
                   ORDER BY PKP.ProductPriority
                """

        res = list()
        for row in conn.select(query):
            nav = NavigationProduct(row.get_entry("NavId"),
                                    row.get_entry("ClassCode"),
                                    row.get_entry("ProductCode"),
                                    row.get_entry("ProductName"),
                                    row.get_entry("ButtonColor"))
            res.append(nav)

        return res

    return BaseRepository(mb_context).execute_with_connection(inner_func)
