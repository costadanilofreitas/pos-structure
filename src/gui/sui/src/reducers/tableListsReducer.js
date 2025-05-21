import { ensureArray } from '3s-posui/utils'

import { TableStatus } from '../app/model/TableStatus'
import TableType from '../app/model/TableType'
import { STORE_MODIFIED } from '../constants/actionTypes'

function createEmptyLists() {
  const ret = {
    tabs: []
  }
  ret[0] = []
  ret[TableStatus.Available] = []
  ret[TableStatus.InProgress] = []
  ret[TableStatus.Totalized] = []
  ret[TableStatus.Closed] = []

  return ret
}

function orderTables(ret) {
  Object.entries(ret).forEach(([, index]) => {
    index.sort(function (a, b) {
      return a.id - b.id || a.tabId - b.tabId
    })
  })

  return ret
}

export default function (state, action) {
  if (action && action.type && action.type === STORE_MODIFIED) {
    const tables = ensureArray(action.payload.Tables.Table)
    const ret = createEmptyLists()
    tables.forEach(table => {
      if (table != null) {
        const createdTable = {
          id: table['@attributes'].id,
          seats: parseInt(table['@attributes'].seats, 10),
          serviceSeats: null,
          status: parseInt(table['@attributes'].status, 10),
          statusDescr: table['@attributes'].statusDescr,
          type: parseInt(table['@attributes'].type, 10),
          typeDescr: table['@attributes'].typeDescr,
          userId: table['@attributes'].userId,
          startTS: table['@attributes'].startTS,
          lastUpdateTS: table['@attributes'].lastUpdateTS,
          tabId: table.Properties != null ? table.Properties['@attributes'].TAB_ID : '',
          ordersHoldItems: table.Properties != null && table.Properties['@attributes'].ORDERS_HOLD_ITEMS != null
            ? table.Properties['@attributes'].ORDERS_HOLD_ITEMS
            : ''
        }

        if (table.Properties && table.Properties.tabNumber) {
          createdTable.tabNumber = table.Properties.tabNumber
        }

        if (table['@attributes'].serviceSeats) {
          createdTable.serviceSeats = parseInt(table['@attributes'].serviceSeats, 10)
        }

        if (table['@attributes'].currentPOSId) {
          createdTable.currentPOSId = parseInt(table['@attributes'].currentPOSId, 10)
        }

        if (createdTable.type === TableType.Tab) {
          ret.tabs.push(createdTable)
          return
        }

        ret[0].push(createdTable)
        switch (createdTable.status) {
          case TableStatus.InProgress:
          case TableStatus.Seated:
          case TableStatus.Waiting2BSeated:
            ret[TableStatus.InProgress].push(createdTable)
            break
          case TableStatus.Totalized:
            ret[TableStatus.Totalized].push(createdTable)
            break
          case TableStatus.Closed:
            ret[TableStatus.Closed].push(createdTable)
            break
          case TableStatus.Available:
            ret[TableStatus.Available].push(createdTable)
            break
          default:
            break
        }
      }
    })

    return orderTables(ret)
  }

  if (state) {
    return state
  }

  return createEmptyLists()
}
