import { TRAINING_MODE } from '../constants/actionTypes'

export default function (state = false, action = null) {
  switch (action.type) {
    case TRAINING_MODE:
      return action.payload
    default:
  }

  return state
}
