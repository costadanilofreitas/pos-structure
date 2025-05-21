import _ from 'lodash'
import { PROD_VIEW_UPDATE } from '../constants/actionTypes'

const sortOrders = (orders) => {
  orders.sort((orderA, orderB) => {
    const seqA = (orderA.attrs || {}).prod_sequence
    const seqB = (orderB.attrs || {}).prod_sequence
    if (seqA < seqB) {
      return -1
    }
    if (seqA > seqB) {
      return 1
    }
    return 0
  })
  return orders
}

export default function (state = [], action = null) {
  switch (action.type) {
    case PROD_VIEW_UPDATE: {
      const prodOrder = action.payload
      const attrs = prodOrder.attrs || {}
      if (!attrs.order_id) {
        return state
      }
      const idx = _.findIndex(state, { attrs: { order_id: attrs.order_id } })
      if (idx !== -1) {
        if (attrs.prod_state === 'SERVED') {
          // order has been served, remove it from the list
          return [...state.slice(0, idx), ...state.slice(idx + 1)]
        }
        // replace existing order
        return [...state.slice(0, idx), prodOrder, ...state.slice(idx + 1)]
      }
      return sortOrders([...state, prodOrder])
    }
    default:
  }

  return state
}
