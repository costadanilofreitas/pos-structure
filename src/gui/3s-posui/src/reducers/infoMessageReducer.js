import { INFO_MESSAGE_CHANGED, DISMISS_INFO_MESSAGE } from '../constants/actionTypes'

export default function (state = null, action = null) {
  switch (action.type) {
    case INFO_MESSAGE_CHANGED:
      return action.payload || {}
    case DISMISS_INFO_MESSAGE:
      return {}
    default:
  }

  return state
}
