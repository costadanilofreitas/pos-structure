import { CASH_DRAWER_CHANGED } from '../constants/actionTypes'

export default function (state = null, action = null) {
  switch (action.type) {
    case CASH_DRAWER_CHANGED:
      return (action.payload || {}).status !== 'CLOSED'
    default:
  }
  return state
}
