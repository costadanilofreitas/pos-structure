import _ from 'lodash'

import { ORDER_CHANGED } from '3s-posui/constants/actionTypes'
import { ensureArray } from '3s-posui/utils'


export default function (state = {}, action = null) {
  if (action.type === ORDER_CHANGED) {
    if (_.has(action.payload, '@attributes')) {
      Object.keys(action.payload['@attributes']).forEach(k => {
        action.payload[k] = action.payload['@attributes'][k]
      })
    }
    if (_.has(action.payload, 'SaleLine')) {
      action.payload.SaleLine = ensureArray(action.payload.SaleLine)
      _.forEach((action.payload.SaleLine), (line) =>
        Object.keys(line['@attributes']).forEach(k => {
          line[k] = line['@attributes'][k]
        }))
    }
    if (_.has(action.payload, 'TenderHistory')) {
      if (action.payload.TenderHistory != null && action.payload.TenderHistory.Tender != null) {
        action.payload.TenderHistory.Tender = ensureArray(action.payload.TenderHistory.Tender)
        _.forEach((action.payload.TenderHistory.Tender), (line) =>
          Object.keys(line['@attributes']).forEach(k => {
            line[k] = line['@attributes'][k]
          }))
      }
    }
    return action.payload
  }

  return state
}
