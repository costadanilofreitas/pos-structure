import { NAVIGATION_DATA_LOADED, RESYNC } from '3s-posui/constants/actionTypes'


export default function (state, action = null) {
  if (action && action.type && action.type === RESYNC) {
    return null
  }

  if (action && action.type && action.type === NAVIGATION_DATA_LOADED) {
    return action.payload || {}
  }

  if (state) {
    return state
  }

  return null
}
