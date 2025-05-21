export default function tableInfoReducer(state, action) {
  if (action && action.type) {
    if (action.type === 'TABLE_INFO_CHANGED') {
      return action.payload
    }
  }

  if (state != null) {
    return state
  }

  return false
}
