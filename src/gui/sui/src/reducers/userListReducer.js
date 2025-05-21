import { RESYNC } from '3s-posui/constants/actionTypes'
import { USER_DATA_LOADED } from '../constants/actionTypes'

export default function userListReducer(state, action) {
  if (action && action.type && action.type === RESYNC) {
    return null
  }

  if (action.type === USER_DATA_LOADED) {
    return action.payload
  }

  if (state != null) {
    return state
  }

  return null
}
