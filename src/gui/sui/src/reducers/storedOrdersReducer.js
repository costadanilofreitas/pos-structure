import { RESYNC } from '3s-posui/constants/actionTypes'
import { STORED_ORDERS_CHANGED } from '../constants/actionTypes'


export default function (state = null, action = null) {
  if (action && action.type && action.type === RESYNC) {
    return null
  }

  if (action && action.type && action.type === STORED_ORDERS_CHANGED) {
    if (action.payload) {
      return action.payload
    }
    return null
  }

  if (state) {
    return state
  }
  return null
}
