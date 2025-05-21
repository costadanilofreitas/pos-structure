import { MODIFIERS_DATA_CHANGED } from '../constants/actionTypes'

export default function (state = {}, action = null) {
  switch (action.type) {
    case MODIFIERS_DATA_CHANGED:
      return { ...state, ...action.payload }
    default:
  }

  return state
}
