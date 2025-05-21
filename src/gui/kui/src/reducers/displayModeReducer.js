import { SET_DISPLAY_MODE } from '../constants/actionTypes'

export default function (state = '', action = null) {
  if (action.type === SET_DISPLAY_MODE) {
    return action.payload
  }

  return state
}
