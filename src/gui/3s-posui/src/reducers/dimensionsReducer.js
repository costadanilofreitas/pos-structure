import { DIMENSIONS_LOADED } from '../constants/actionTypes'

export default function (state = null, action = null) {
  switch (action.type) {
    case DIMENSIONS_LOADED:
      return action.payload
    default:
  }

  return state
}
