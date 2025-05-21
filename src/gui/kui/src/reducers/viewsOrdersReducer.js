import { RESYNC } from '3s-posui/constants/actionTypes'
import { parseISO8601Date } from '3s-posui/utils'

import { SET_VIEWS_ORDERS } from '../constants/actionTypes'
import OrderAttributes from '../app/model/OrderAttributes'
import OrderData from '../app/model/OrderData'
import Item from '../app/model/Item'
import Line from '../app/model/Line'

function createItem(item, orderState, orderSendMoment) {
  let sendMoment = item.attrs.send_moment ? parseISO8601Date(item.attrs.send_moment) : null
  if (orderState === 'VOIDED') {
    sendMoment = orderSendMoment
  }

  const lastUpdated = parseISO8601Date(item.attrs.last_updated)

  return new Item(
    parseInt(item.attrs.line_number, 10),
    item.attrs.item_id,
    parseInt(item.attrs.part_code, 10),
    parseFloat(item.attrs.level),
    parseFloat(item.attrs.pos_level),
    item.attrs.item_type,
    parseFloat(item.attrs.qty),
    parseFloat(item.attrs.default_qty),
    parseFloat(item.attrs.multiplied_qty),
    item.attrs.description,
    item,
    item.tags,
    item.tagHistory,
    item.comments,
    item.attrs.wait_time,
    sendMoment,
    parseFloat(item.attrs.prep_time),
    orderState,
    lastUpdated)
}

function createLine(prodOrder) {
  if (prodOrder == null) {
    return null
  }

  const orderAttributes = new OrderAttributes(
    parseInt(prodOrder.attrs.order_id, 10),
    prodOrder.attrs.prod_state,
    prodOrder.attrs.display_time_gmt !== undefined && prodOrder.attrs.display_time_gmt !== '' ?
      parseISO8601Date(prodOrder.attrs.display_time_gmt, true) :
      parseISO8601Date(prodOrder.attrs.created_at),
    prodOrder.attrs.prod_sequence,
    prodOrder.attrs.sale_type)
  const orderData = new OrderData(orderAttributes, prodOrder.props)

  let orderSendMoment = null
  const stateHistoryLength = prodOrder.stateHistory.length
  if (stateHistoryLength > 0 && prodOrder.stateHistory[stateHistoryLength - 1].state === 'VOIDED') {
    orderSendMoment = prodOrder.stateHistory[stateHistoryLength - 1].timestamp
  }

  const line = new Line(orderData)
  prodOrder.items.forEach(item => {
    line.items.push(createItem(item, prodOrder.attrs.state, orderSendMoment))
  })

  return line
}

function createLines(orders) {
  const ordersLines = {}
  for (let i = 0; i < orders.length; i++) {
    const order = orders[i]
    const orderId = order.attrs.order_id
    for (let j = 0; j < order.items.length; j++) {
      const item = order.items[j]
      const itemKey = `${orderId}_${item.attrs.line_number}`
      if (ordersLines[itemKey] == null) {
        const newOrder = JSON.parse(JSON.stringify(order))
        newOrder.items = [item]
        ordersLines[itemKey] = newOrder
      } else {
        ordersLines[itemKey].items.push(item)
      }
    }
  }

  const lines = []
  Object.keys(ordersLines).forEach(function (key) {
    const items = ordersLines[key]
    const line = createLine(items)
    if (line != null) {
      lines.push(createLine(items))
    }
  })
  return lines
}

export default function (state = {}, action = null) {
  switch (action.type) {
    case SET_VIEWS_ORDERS: {
      const newState = { ...state }
      const orders = action.payload.value

      const lines = createLines(orders)

      newState[action.payload.key] = { orders: orders, lines: lines }
      return newState
    }
    case RESYNC:
      return {}
    default:
  }

  return state
}
