import { POS_STATE_CHANGED, CUSTOM_CHANGED } from '3s-posui/constants/actionTypes'

export default function (state = null, action = null) {
  switch (action.type) {
    case POS_STATE_CHANGED:
      return action.payload
    case CUSTOM_CHANGED:
      if (action.payload.POS_MUST_BE_BLOCKED != null && action.payload.POS_MUST_BE_BLOCKED.toLowerCase() === 'true') {
        return {
          ...state,
          state: 'BLOCKED'
        }
      }
      break
    default:
  }

  return state
}
