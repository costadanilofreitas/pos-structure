import { SET_ORDER_PAGE } from '../constants/actionTypes'

const DEFAULT_ORDER_PAGE = 1

export default function (state = DEFAULT_ORDER_PAGE, action = null) {
  if (action.type === SET_ORDER_PAGE) {
    return action.payload
  }

  return state
}
