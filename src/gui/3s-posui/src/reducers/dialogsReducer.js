import { DIALOGS_CHANGED, DIALOG_CLOSED, RESYNC } from '../constants/actionTypes'

const DEFAULT_DIALOGS_STATE = []

export default function (state = DEFAULT_DIALOGS_STATE, action = null) {
  switch (action.type) {
    case DIALOGS_CHANGED:
      return action.payload
    case DIALOG_CLOSED:
      if (state && state.length > 0) {
        return state.filter(obj => obj.id !== action.payload)
      }
      break
    case RESYNC:
      return DEFAULT_DIALOGS_STATE
    default:
  }

  return state
}
