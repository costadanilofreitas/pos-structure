import { CUSTOM_CHANGED } from '../constants/actionTypes'

export default function (state = null, action = null) {
  switch (action.type) {
    case CUSTOM_CHANGED:
      return { ...(state || {}), ...action.payload }
    default:
  }

  return state
}
