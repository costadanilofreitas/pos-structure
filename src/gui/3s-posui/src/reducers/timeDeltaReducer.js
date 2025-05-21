import { TIME_DELTA } from '../constants/actionTypes'

export default function (state = 0, action = null) {
  switch (action.type) {
    case TIME_DELTA:
      return action.payload
    default:
  }

  return state
}
