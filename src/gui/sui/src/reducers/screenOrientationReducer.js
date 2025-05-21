import { RESYNC } from '3s-posui/constants/actionTypes'
import { UPDATING_WINDOW_SIZE } from '../constants/actionTypes'
import ScreenOrientation from '../constants/ScreenOrientation'


export default function (state = null, action = null) {
  if (action && action.type && action.type === RESYNC) {
    return null
  }

  if (action && action.type && action.type === UPDATING_WINDOW_SIZE) {
    if (action.width && action.height) {
      return action.width > action.height ? ScreenOrientation.Landscape : ScreenOrientation.Portrait
    }
    return ScreenOrientation.Landscape
  }

  if (state) {
    return state
  }
  return null
}
