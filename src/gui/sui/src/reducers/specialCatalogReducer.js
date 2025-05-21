import { CUSTOM_CHANGED } from '3s-posui/constants/actionTypes'

export default function specialCatalogReducer(state, action) {
  if (action && action.type && action.type === CUSTOM_CHANGED) {
    if (action.payload && action.payload['Special Catalog Enabled']) {
      return action.payload['Special Catalog Enabled']
    }
    return null
  }

  if (state) {
    return state
  }
  return null
}
