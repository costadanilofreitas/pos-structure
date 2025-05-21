import _ from 'lodash'
import * as types from '../constants/actionTypes'

/**
 * Logs for usability study
 */
const loggingMiddleware = store => next => action => {
  const state = store.getState() || {}
  const order = state.order || {}
  const atts = order['@attributes'] || {}
  const orderId = atts.orderId || 'none'
  const orderState = atts.state || 'none'

  let line = {}
  switch (action.type) {
    case types.DIALOGS_CHANGED:
      line.dlg = ((action.payload || [])[0]) || {}
      break
    case types.DIALOG_CLOSED:
      line.dlg = action.payload
      break
    case types.BUTTON_DOWN:
      line.text = action.payload.text
      break
    case types.BUTTON_UP:
      line.text = action.payload.text
      line.clicked = action.payload.clicked
      break
    default:
      break
  }
  if (!_.isEmpty(line)) {
    line.action = action.type
    line.orderId = orderId
    line.orderStat = orderState
    line = JSON.stringify(line)
    if (window.mwapp && window.mwapp.log) {
      window.mwapp.log(line)
    }
  }
  return next(action)
}

export default loggingMiddleware
