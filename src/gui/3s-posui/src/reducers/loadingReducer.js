import { EVENT_LOOP_STATE, I18N_LOADED, RESYNC } from '../constants/actionTypes'

const DEFAULT_LOADING_STATE = {
  synched: false,
  conflict: false,
  localeLoaded: false
}

export default function (state = DEFAULT_LOADING_STATE, action = null) {
  switch (action.type) {
    case EVENT_LOOP_STATE: {
      const loopState = action.payload || {}
      return {
        ...state,
        synched: Boolean(loopState.syncId),
        conflict: Boolean(loopState.conflict)
      }
    }
    case RESYNC: {
      return {
        ...state,
        synched: false
      }
    }
    case I18N_LOADED: {
      return { ...state, localeLoaded: true }
    }
    default:
  }

  return state
}
