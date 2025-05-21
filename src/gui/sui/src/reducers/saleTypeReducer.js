import { CHANGE_SALE_TYPE } from '../constants/actionTypes'

export default function (state = null, action = null) {
  if (action.type === CHANGE_SALE_TYPE) {
    return action.saleType
  }

  return state
}
