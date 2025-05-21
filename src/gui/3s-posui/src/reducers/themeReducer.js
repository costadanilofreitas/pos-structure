import { SET_THEME, THEME_CONFIGURATION_CHANGED, CURRENT_THEME_CHANGED } from '../constants/actionTypes'

export default function (state = {}, action = null) {
  let defaultThemeName = null
  let defaultTheme = null

  switch (action.type) {
    case SET_THEME:
      return action.payload
    case THEME_CONFIGURATION_CHANGED:
      defaultThemeName = action.payload.defaultTheme
      defaultTheme = action.payload.themes.find(x => x.name === defaultThemeName)
      if (defaultTheme == null) {
        return { ...state, themes: [state].concat(action.payload.themes) }
      }

      return { ...state, ...defaultTheme, name: defaultThemeName, themes: [state].concat(action.payload.themes) }
    case CURRENT_THEME_CHANGED:
      defaultThemeName = action.payload
      defaultTheme = state.themes.find(x => x.name === defaultThemeName)
      if (defaultTheme == null) {
        return state
      }

      return { ...state, ...defaultTheme, name: defaultThemeName }
    default:
      break
  }

  return state
}
