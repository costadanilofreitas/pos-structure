import { SET_THEME } from '../constants/actionTypes'

export default function setThemeAction(theme) {
  return {
    type: SET_THEME,
    payload: theme
  }
}
