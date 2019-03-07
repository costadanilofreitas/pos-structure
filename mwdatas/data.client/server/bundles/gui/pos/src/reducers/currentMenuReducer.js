import { ORDER_CHANGED, ORDER_STARTED, ORDER_PAID, ORDER_STORED } from 'posui/constants/actionTypes'
import { CHANGE_CURRENT_MENU } from '../constants/actionTypes'
import { MENU_UNSELECTED, MENU_PAYMENT, MENU_ORDER, MENU_DASHBOARD } from './menuReducer'

export default function (state = MENU_UNSELECTED, action) {
  switch (action.type) {
  case ORDER_STARTED:
  case ORDER_PAID:
  case ORDER_STORED:
    return MENU_ORDER
  case ORDER_CHANGED: {
    const order = action.payload || {}
    const attributes = order['@attributes'] || {}
    switch (attributes.state) {
    case 'TOTALED':
      return MENU_PAYMENT
    case 'IN_PROGRESS':
    case 'VOIDED':
      return MENU_ORDER
    default:
      return (state === MENU_UNSELECTED) ? MENU_DASHBOARD : state
    }
  }
  case CHANGE_CURRENT_MENU:
    return action.payload
  default:
  }

  return state
}
