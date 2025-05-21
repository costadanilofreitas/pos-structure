import { TEF_AVAILABLE_CHANGED } from '../constants/actionTypes'

export default function (state = null, action = null) {
  if (action.type === TEF_AVAILABLE_CHANGED) {
    return action.payload
  }

  return state
}
