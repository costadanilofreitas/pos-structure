import { RESYNC } from '3s-posui/constants/actionTypes'
import { SET_CONSOLIDATED_ITEMS } from '../constants/actionTypes'

export default function (state = false, action = null) {
  switch (action.type) {
    case SET_CONSOLIDATED_ITEMS:
      return action.payload
    case RESYNC:
      return false
    default:
  }

  return state
}
