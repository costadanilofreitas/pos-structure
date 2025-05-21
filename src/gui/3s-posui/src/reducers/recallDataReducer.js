import { RECALL_DATA_CHANGED } from '../constants/actionTypes'

export default function (state = {}, action = null) {
  switch (action.type) {
    case RECALL_DATA_CHANGED:
      return action.payload
    default:
  }

  return state
}
