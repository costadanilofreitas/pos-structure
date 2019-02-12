export const MENU_UNSELECTED = 0
export const MENU_DASHBOARD = 1
export const MENU_ORDER = 2
export const MENU_SAVED_ORDERS = 3
export const MENU_PAYMENT = 4
export const MENU_MANAGER = 5

export default function () {
  return [
    {
      'id': MENU_DASHBOARD,
      'text': '$DASHBOARD',
      'defaultText': 'Dashboard'
    },
    {
      'id': MENU_ORDER,
      'text': '$ORDER',
      'defaultText': 'Order'
    },
    {
      'id': MENU_SAVED_ORDERS,
      'text': '$SAVED_ORDERS',
      'defaultText': 'Saved Orders'
    },
    {
      'id': MENU_PAYMENT,
      'text': '$PAYMENT',
      'defaultText': 'Payment'
    },
    {
      'id': MENU_MANAGER,
      'text': '$MANAGER',
      'defaultText': 'Manager'
    }
  ]
}
