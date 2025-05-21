import { RESYNC } from '3s-posui/constants/actionTypes'
import { STATIC_CONFIG_LOADED } from '../constants/actionTypes'


export default function staticConfigReducer(state, action) {
  if (action && action.type && action.type === RESYNC) {
    return null
  }

  if (action && action.type && action.type === STATIC_CONFIG_LOADED) {
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
