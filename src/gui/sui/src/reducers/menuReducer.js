import { RESYNC } from '3s-posui/constants/actionTypes'
import { CHANGE_MENU } from '../constants/actionTypes'

export default function menuReducer(state, action) {
  if (action && action.type && action.type === RESYNC) {
    return null
  }

  if (action.type === CHANGE_MENU) {
    return action.payload
  }

  if (state != null) {
    return state
  }

  return null
}
