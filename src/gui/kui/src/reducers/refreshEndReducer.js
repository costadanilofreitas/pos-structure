import { KDS_REFRESH_END, KDS_REFRESH_START } from '../constants/actionTypes'

export default function (state = false, action = null) {
  if (action.type === KDS_REFRESH_END) {
    return true
  }
  if (action.type === KDS_REFRESH_START) {
    return false
  }

  return state
}
