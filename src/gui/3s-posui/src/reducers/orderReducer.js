import { ORDER_CHANGED } from '../constants/actionTypes'

export default function (state = {}, action = null) {
  switch (action.type) {
    case ORDER_CHANGED:
      return action.payload
    default:
  }

  return state
}
