import { OPERATOR_CHANGED, RESYNC } from '3s-posui/constants/actionTypes'
import { SET_OPERATOR_LEVEL } from '../constants/actionTypes'
import { ensureArray } from '../util/renderUtil'


export default function (state, action = null) {
  if (action && action.type && action.type === RESYNC) {
    return null
  }

  if (action && action.type && action.type === OPERATOR_CHANGED) {
    if (action.payload == null && state == null) {
      return {}
    }

    if (_.has(action.payload, '@attributes')) {
      Object.keys(action.payload['@attributes']).forEach(k => {
        action.payload[k] = action.payload['@attributes'][k]
      })
    }

    return action.payload || {}
  }

  if (action && action.type && action.type === SET_OPERATOR_LEVEL) {
    if (action.payload != null && state != null) {
      const operators = action.payload.Operator != null ? action.payload.Operator : []
      const newOperator = ensureArray(operators).find(x => x['@attributes'].id === state.id)
      if (newOperator != null) {
        return { ...state, level: newOperator['@attributes'].level }
      }
    }
  }

  if (state) {
    return state
  }

  return null
}
