import { RESYNC } from '3s-posui/constants/actionTypes'
import { PRODUCT_DATA_LOADED } from '../constants/actionTypes'


export default function (state = null, action = null) {
  if (action && action.type && action.type === RESYNC) {
    return null
  }

  if (action && action.type && action.type === PRODUCT_DATA_LOADED) {
    return action.payload || []
  }

  return state
}
