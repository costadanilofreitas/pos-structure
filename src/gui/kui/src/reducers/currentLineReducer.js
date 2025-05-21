import { SET_CURRENT_LINE, SET_DISPLAY_MODE } from '../constants/actionTypes'

const UNSELECTED_LINE = 0

export default function (state = UNSELECTED_LINE, action = null) {
  if (action.type === SET_CURRENT_LINE) {
    return action.payload
  }

  if (action.type === SET_DISPLAY_MODE) {
    return 0
  }

  return state
}
