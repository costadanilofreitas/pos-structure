import { RESYNC } from '3s-posui/constants/actionTypes'
import { parseXml, xmlToJson } from '3s-posui/utils/xml'
import { TABLE_MODIFIED, TABLE_SELECTED } from '../constants/actionTypes'
import { ensureArray } from '../util/renderUtil'


function parseBusinessPeriod(businessPeriod) {
  const isoDate = `${businessPeriod.substr(0, 4)}-${businessPeriod.substr(4, 2)}-${businessPeriod.substr(6, 2)}`
  return new Date(Date.parse(isoDate))
}

function parseOrderAttributes(orderJson) {
  const orderAttr = orderJson['@attributes']

  return {
    '@attributes': orderAttr,
    orderId: parseInt(orderAttr.orderId, 10),
    stateId: parseInt(orderAttr.stateId, 10),
    state: orderAttr.state,
    typeId: parseInt(orderAttr.typeId, 10),
    type: orderAttr.type,
    originatorId: orderAttr.originatorId,
    lineCounter: parseInt(orderAttr.lineCounter, 10),
    createdAt: new Date(Date.parse(orderAttr.createdAt)),
    lastNewLineAt: new Date(orderAttr.lastNewLineAt),
    businessPeriod: parseBusinessPeriod(orderAttr.businessPeriod),
    podType: orderAttr.podType,
    sessionId: orderAttr.sessionId,
    totalAmount: parseFloat(orderAttr.totalAmount),
    totalAfterDiscount: parseFloat(orderAttr.totalAfterDiscount),
    totalGross: parseFloat(orderAttr.totalGross),
    totalTender: parseFloat(orderAttr.totalTender),
    change: parseFloat(orderAttr.change),
    dueAmount: parseFloat(orderAttr.dueAmount),
    priceList: orderAttr.priceList,
    priceBasis: orderAttr.priceBasis,
    saleType: parseInt(orderAttr.saleType, 10),
    lastModifiedLine: parseInt(orderAttr.lastModifiedLine, 10),
    taxTotal: parseFloat(orderAttr.taxTotal),
    major: parseInt(orderAttr.major, 10),
    minor: parseInt(orderAttr.minor, 10),
    discountAmount: parseFloat(orderAttr.discountAmount),
    saleTypeDescr: orderAttr.saleTypeDescr,
    createdAtGMT: new Date(Date.parse(`${orderAttr.createdAtGMT}Z`)),
    lastNewLineAtGMT: new Date(Date.parse(orderAttr.lastNewLineAtGMT)),
    orderDiscountAmount: parseFloat(orderAttr.orderDiscountAmount),
    tip: parseFloat(orderAttr.tip),
    seat: null,
    saleLines: []
  }
}

function parseSaleLine(saleLineJson) {
  const saleLineAttr = saleLineJson['@attributes']

  const saleLine = {
    '@attributes': saleLineAttr,
    lineNumber: parseInt(saleLineAttr.lineNumber, 10),
    itemId: saleLineAttr.itemId,
    level: parseFloat(saleLineAttr.level),
    partCode: parseInt(saleLineAttr.partCode, 10),
    productName: saleLineAttr.productName,
    qty: parseFloat(saleLineAttr.qty),
    decQty: parseFloat(saleLineAttr.decQty),
    incQty: parseFloat(saleLineAttr.incQty),
    multipliedQty: parseFloat(saleLineAttr.multipliedQty),
    itemType: saleLineAttr.itemType,
    itemPrice: saleLineAttr.itemPrice ? parseFloat(saleLineAttr.itemPrice) : null,
    unitPrice: saleLineAttr.unitPrice ? parseFloat(saleLineAttr.unitPrice) : null,
    addedUnitPrice: saleLineAttr.addedUnitPrice ? parseFloat(saleLineAttr.addedUnitPrice) : null,
    jsonArrayTags: saleLineAttr.jsonArrayTags,
    measureUnit: saleLineAttr.measureUnit,
    productPriority: parseInt(saleLineAttr.productPriority, 10),
    priceKey: saleLineAttr.priceKey ? saleLineAttr.priceKey : null,
    defaultQty: saleLineAttr.defaultQty ? parseFloat(saleLineAttr.defaultQty) : null,
    minQty: saleLineAttr.minQty ? parseFloat(saleLineAttr.minQty) : null,
    maxQty: saleLineAttr.maxQty ? parseFloat(saleLineAttr.maxQty) : null,
    seat: null,
    fractionFrom: null,
    hold: false
  }

  if (saleLineAttr.customProperties) {
    const a = saleLineAttr.customProperties
    const obj = JSON.parse(a)
    saleLine.seat = obj.seat ? parseInt(obj.seat, 10) : null
    saleLine.hold = obj.hold ? obj.hold : null

    if (obj.OMGR_FRACTION_FROM_LINE) {
      saleLine.fractionFrom = obj.OMGR_FRACTION_FROM_LINE
    }
  }

  return saleLine
}

function parseOrderSaleLines(orderJson) {
  const parsedSaleLines = []
  if (orderJson.SaleLine) {
    const saleLines = ensureArray(orderJson.SaleLine)
    for (let j = 0; j < saleLines.length; j++) {
      parsedSaleLines.push(parseSaleLine(saleLines[j]))
    }
  }

  return parsedSaleLines
}

function parseOrderStateHistory(orderJson) {
  const states = []

  if (orderJson.StateHistory && orderJson.StateHistory.State) {
    const statesJson = ensureArray(orderJson.StateHistory.State)
    for (let i = 0; i < statesJson.length; i++) {
      states.push(statesJson[i])
    }
  }

  return states.length === 0 ? {} : { State: states }
}

function parseTableOrder(orderJson) {
  const order = parseOrderAttributes(orderJson)

  order.SaleLine = ensureArray(orderJson.SaleLine)
  order.saleLines = parseOrderSaleLines(orderJson)

  order.StateHistory = parseOrderStateHistory(orderJson)
  return order
}

function parseServiceTender(tenderJson) {
  const tenderAttr = tenderJson['@attributes']

  return {
    '@attributes': tenderAttr,
    id: parseInt(tenderAttr.serviceTenderId, 10),
    orderId: parseInt(tenderAttr.orderId, 10),
    tenderTypeId: parseInt(tenderAttr.tenderId, 10),
    serviceId: parseInt(tenderAttr.serviceId, 10),
    amount: parseFloat(tenderAttr.tenderAmount),
    timestamp: new Date(Date.parse(`${tenderAttr.timestamp}Z`)),
    detail: tenderAttr.tenderDetail,
    changeAmount: tenderAttr.changeAmount ? parseFloat(tenderAttr.changeAmount) : 0.0
  }
}

function parseServiceTenders(tableJson) {
  const parsedTenders = []

  if (tableJson.ServiceTenders) {
    const tendersJson = ensureArray(tableJson.ServiceTenders.ServiceTender)
    for (let i = 0; i < tendersJson.length; i++) {
      parsedTenders.push(parseServiceTender(tendersJson[i]))
    }
  }

  return parsedTenders
}

function parseTableOrders(tableJson) {
  const parsedOrders = []

  if (tableJson.Orders && tableJson.Orders.Order) {
    const ordersJson = ensureArray(tableJson.Orders.Order)
    for (let i = 0; i < ordersJson.length; i++) {
      parsedOrders.push(parseTableOrder(ordersJson[i]))
    }
  }

  return parsedOrders
}

function parseTableAttributes(tableJson) {
  const tableAttr = tableJson['@attributes']

  const table = {
    id: tableAttr.id,
    type: parseInt(tableAttr.type, 10),
    typeDescr: tableAttr.typeDescr,
    seats: parseInt(tableAttr.seats, 10),
    status: parseInt(tableAttr.status, 10),
    statusDescr: tableAttr.statusDescr,
    serviceId: tableAttr.serviceId ? parseInt(tableAttr.serviceId, 10) : null,
    businessPeriod: tableAttr.businessPeriod ? new Date(Date.parse(tableAttr.businessPeriod)) : null,
    userId: tableAttr.userId,
    serviceSeats: tableAttr.serviceSeats ? parseInt(tableAttr.serviceSeats, 10) : null,
    sector: tableAttr.sector,
    startTS: tableAttr.startTS ? new Date(Date.parse(`${tableAttr.startTS}Z`)) : null,
    lastUpdateTS: tableAttr.lastUpdateTS ? new Date(Date.parse(`${tableAttr.lastUpdateTS}Z`)) : null,
    finishTS: tableAttr.finishTS ? new Date(Date.parse(`${tableAttr.finishTS}Z`)) : null,
    currentPOSId: tableAttr.currentPOSId ? parseInt(tableAttr.currentPOSId, 10) : null,
    totalAmount: tableAttr.totalAmount ? parseFloat(tableAttr.totalAmount) : null,
    totalPerSeat: tableAttr.totalPerSeat ? parseFloat(tableAttr.totalPerSeat) : null,
    dueAmount: tableAttr.dueAmount ? parseFloat(tableAttr.dueAmount) : null,
    tabNumber: null,
    linkedTables: tableAttr.linkedTables ? tableAttr.linkedTables.split(',') : [],
    changeAmount: tableAttr.changeAmount ? parseFloat(tableAttr.changeAmount) : null,
    orders: [],
    serviceTenders: []
  }

  if (tableJson.Properties) {
    const properties = tableJson.Properties['@attributes']
    if (properties.TAB_ID) {
      table.tabNumber = properties.TAB_ID
    }
    if (properties.SpecialCatalog) {
      table.specialCatalog = properties.SpecialCatalog
    }
  }

  return table
}

function parseTable(tableJson) {
  const table = parseTableAttributes(tableJson)
  table.orders = parseTableOrders(tableJson)
  table.serviceTenders = parseServiceTenders(tableJson)
  return table
}

export default function (state, action) {
  let tableJson
  if (action && action.type) {
    switch (action.type) {
      case RESYNC: {
        return null
      }
      case TABLE_SELECTED: {
        if (action.payload == null || action.payload === '0' || action.payload === 0) {
          return null
        }
        tableJson = xmlToJson(parseXml(action.payload)).Table
        break
      }
      case TABLE_MODIFIED: {
        if (action.payload == null || action.payload.Table == null) {
          return null
        }
        tableJson = action.payload.Table
        break
      }
      default:
        break
    }
  }

  if (tableJson != null) {
    return parseTable(tableJson)
  }

  if (state) {
    return state
  }

  return null
}
