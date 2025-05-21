import { ensureArray } from './renderUtil'
import { orderNotInState } from '../app/util/orderValidator'
import OrderState from '../app/model/OrderState'

export function getLastSaleLine(order) {
  let maxLineNumber = -1
  let lastSaleLine = null
  if (order != null && order.SaleLine != null && orderNotInState(order, OrderState.Paid, OrderState.Voided)) {
    ensureArray(order.SaleLine).forEach(saleLine => {
      if (saleLine['@attributes'].level === '0' &&
        parseFloat(saleLine['@attributes'].qty) > 0 &&
        parseInt(saleLine['@attributes'].lineNumber, 10) > maxLineNumber) {
        lastSaleLine = saleLine
        maxLineNumber = parseInt(saleLine['@attributes'].lineNumber, 10)
      }
    })
  }
  return lastSaleLine
}

export function lastGroupSaleLine(order) {
  const groupBY = key => array =>
    array.reduce(
      (objectsByKeyValue, obj) => ({
        ...objectsByKeyValue,
        [obj['@attributes'][key]]: (objectsByKeyValue[obj['@attributes'][key]] || []).concat(obj)
      }),
      {}
    )
  let lastSaleLineGrouped = null
  if (order != null && order.SaleLine != null) {
    const groupedSaleLine = Object.values(groupBY('lineNumber')(order.SaleLine))
    let maxLineNumber = -1
    groupedSaleLine.forEach((saleLineGrouped) => {
      saleLineGrouped.forEach(saleLine => {
        if (saleLine['@attributes'].level === '0' &&
          parseFloat(saleLine['@attributes'].qty) > 0 &&
          parseInt(saleLine['@attributes'].lineNumber, 10) > maxLineNumber) {
          lastSaleLineGrouped = saleLineGrouped
          maxLineNumber = parseInt(saleLine['@attributes'].lineNumber, 10)
        }
      })
    })
  }
  return lastSaleLineGrouped
}

export function addAttributesToObject(order) {
  Object.keys(order['@attributes']).forEach(key => {
    order[key] = order['@attributes'][key]
  })
  return order
}

export function formatOrders(json) {
  const orders = []
  try {
    _.forEach(json, (order) => {
      // convert custom order properties to object
      const custom = {}
      _.forEach(ensureArray((order.custom_properties || {}).OrderProperty || []), (prop) => {
        if (prop.key) {
          custom[prop.key] = prop.value
        }
      })

      _.forEach(order.custom_properties, (value, key) => (custom[key] = value))

      // parse session
      const session = {}
      _.forEach((order.sessionId || '').split(',') || [], (sessionProp) => {
        const splittedSessionProp = sessionProp.split('=') || []
        if (splittedSessionProp.length > 1) {
          session[splittedSessionProp[0]] = splittedSessionProp[1]
        }
      })

      const createdAtTime = order.createdAt ? order.createdAt.split('T')[1] : ''
      orders.push({
        ...order,
        createdAtTime,
        session,
        custom
      })
    })
  } catch (e) {
    console.warn(e)
  }
  return orders
}

export function isDeliveryOrder(customProperties) {
  return customProperties != null && customProperties.REMOTE_ORDER_ID != null
}

export function isLocalDelivery(order) {
  return order.saleTypeDescr.toUpperCase() === 'DELIVERY'
}

export function getAllSaleTypes(saleTypesConfig) {
  const allSaleTypes = []
  for (let i = 0; i < saleTypesConfig.length; i++) {
    allSaleTypes.push(Object.values(saleTypesConfig[i])[0])
  }

  return allSaleTypes
}
