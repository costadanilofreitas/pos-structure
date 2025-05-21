import { SET_CURRENT_ORDER } from '../constants/actionTypes'

const DEFAULT_ORDER_INDEX = 0

export default function (state = DEFAULT_ORDER_INDEX, action = null) {
  if (action.type === SET_CURRENT_ORDER) {
    return action.payload
  }

  return state
}
