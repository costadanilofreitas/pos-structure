import { CASH_DRAWER_CHANGED, FORCE_CASH_DRAWER_CHANGE } from '../constants/actionTypes'

export default function (state = null, action = null) {
  switch (action.type) {
    case CASH_DRAWER_CHANGED:
    case FORCE_CASH_DRAWER_CHANGE:
      return (action.payload || {}).status !== 'CLOSED'
    default:
  }
  return state
}
