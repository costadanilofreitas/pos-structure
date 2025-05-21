import { ORDER_CHANGED_LAST_TIMESTAMP } from '../constants/actionTypes'

export default function (state = null, action = null) {
  switch (action.type) {
    case ORDER_CHANGED_LAST_TIMESTAMP:
      return action.payload
    default:
  }

  return state
}
