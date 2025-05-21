import { SET_DISPLAY_MODE } from '../constants/actionTypes'

export default function setDisplayModeAction(mode) {
  return {
    type: SET_DISPLAY_MODE,
    payload: mode
  }
}
