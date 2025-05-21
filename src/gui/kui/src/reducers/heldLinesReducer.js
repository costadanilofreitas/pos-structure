import { RESYNC } from '3s-posui/constants/actionTypes'
import { SET_HELD_LINES } from '../constants/actionTypes'

export default function (state = [], action = null) {
  switch (action.type) {
    case SET_HELD_LINES:
      return action.payload
    case RESYNC:
      return []
    default:
  }

  return state
}

