import { PRODUCT_DATA_LOADED } from '../constants/actionTypes'

export default function (state = null, action) {
  switch (action.type) {
  case PRODUCT_DATA_LOADED:
    return action.payload || []
  default:
  }

  return state
}
