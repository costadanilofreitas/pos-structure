import { MODIFIERS_LOADED, RESYNC } from '3s-posui/constants/actionTypes'


export default function (state = {}, action = null) {
  if (action && action.type && action.type === RESYNC) {
    return null
  }

  if (action && action.type && action.type === MODIFIERS_LOADED) {
    return action.payload
  }

  return state
}
