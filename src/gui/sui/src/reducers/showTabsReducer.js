import { SHOW_TABS_CHANGED } from '../constants/actionTypes'

export default function showTabsReducer(state, action) {
  if (action && action.type) {
    if (action.type === SHOW_TABS_CHANGED) {
      return action.payload
    }
  }

  if (state != null) {
    return state
  }

  return false
}
