import { POS_STATE_CHANGED } from '../constants/actionTypes'

export default function (state = null, action = null) {
  switch (action.type) {
    case POS_STATE_CHANGED:
      return action.payload
    default:
  }

  return state
}
