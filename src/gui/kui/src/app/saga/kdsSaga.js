import _ from 'lodash'
import { put, select, takeEvery } from 'redux-saga/effects'
import MessageBus from '../../util/MessageBus'
import * as touchTypes from '../../constants/touchTypes'
import OrdersUpdateProcessor from './OrdersUpdateProcessor'
import ItemsServedCommandProcessor from './ItemsServedCommandProcessor'
import OrderDeliveredCommandProcessor from './OrderDeliveredCommandProcessor'
import OrderServedCommandProcessor from './OrderServedCommandProcessor'
import * as eventsType from '../../constants/actionTypes'
import OrderInvalidCommandProcessor from './OrderInvalidCommandProcessor'
import OrderReadyCommandProcessor from './OrderReadyCommandProcessor'
import ItemsDoingCommandProcessor from './ItemsDoingCommandProcessor'
import ItemsDoneCommandProcessor from './ItemsDoneCommandProcessor'
import { SET_CURRENT_LINE, SET_KDS_ZOOM, KDS_REFRESH_START } from '../../constants/actionTypes'

const getViewsOrders = (state) => state.viewsOrders
const getCurrentOrder = (state) => state.currentOrder
const getKdsModel = (state) => state.kdsModel
const getPaginationBlockSize = (state) => state.paginationBlockSize
const getConsolidatedItems = (state) => state.consolidatedItems
const getTimeDelta = (state) => state.timeDelta
const getCurrentLine = (state) => state.currentLine

function getOrderId(order) {
  return order && order.attrs.order_id
}

function calculatedPaginationBlockSize(gridSize, currentOrdersCellArrayIndex) {
  return Math.floor(currentOrdersCellArrayIndex / gridSize) * gridSize
}

function getOrderArrayIndex(ordersArray, orderId, currentOrderPage) {
  if (ordersArray.length === 0) {
    return 0
  }

  return ordersArray.findIndex(order => getOrderId(order) === orderId && order.page === currentOrderPage)
}

function changeCurrentOrderCellSelected(orderIndex, ordersCellArray) {
  let currentOrderIndex = orderIndex
  if (ordersCellArray.length > 0) {
    if (currentOrderIndex < 0) {
      currentOrderIndex = 0
    } else if (currentOrderIndex >= ordersCellArray.length) {
      currentOrderIndex = ordersCellArray.length - 1
    }
  }

  return put({ type: eventsType.SET_CURRENT_ORDER, payload: currentOrderIndex })
}

function changePaginationBlockSize(paginationBlockSize) {
  return put({ type: eventsType.SET_PAGINATION_BLOCK_SIZE, payload: paginationBlockSize })
}

function currentOrderIsLastArrayOrder(currentOrderFirstPageIndex, currentOrderSize, totalCellsInPage) {
  return currentOrderFirstPageIndex + currentOrderSize === totalCellsInPage
}

function currentOrderIsLastPageOrder(
  currentOrdersCellArrayIndex,
  currentOrderSize,
  paginationBlockSize,
  totalCellsInPage
) {
  return currentOrdersCellArrayIndex + currentOrderSize > paginationBlockSize + totalCellsInPage
}

function getNextOrderIndex(
  currentOrdersCellArrayIndex,
  currentOrderFirstPageIndex,
  currentOrderSize,
  totalOrdersCell,
  totalCellsInPage,
  paginationBlockSize,
  isCarousel,
  currentOrderIndex
) {
  const currentPage = Math.floor(currentOrderIndex / totalCellsInPage)
  const currentOrderLastCellIndex = (currentOrderFirstPageIndex + currentOrderSize) - 1
  const currentOrderLastCellPage = Math.floor(currentOrderLastCellIndex / totalCellsInPage)
  const firstCellOnNextPageIndex = (currentPage + 1) * totalCellsInPage

  if (currentOrderIsLastArrayOrder(currentOrderFirstPageIndex, currentOrderSize, totalOrdersCell)) {
    if (currentPage < currentOrderLastCellPage) {
      return firstCellOnNextPageIndex
    }
    return isCarousel ? 0 : totalOrdersCell - 1
  }

  if (currentOrderIsLastPageOrder(currentOrdersCellArrayIndex, currentOrderSize, paginationBlockSize,
    totalCellsInPage) && currentPage < currentOrderLastCellPage) {
    return firstCellOnNextPageIndex
  }

  return currentOrderFirstPageIndex + currentOrderSize
}

function getPreviousOrderIndex(
  currentOrdersCellArrayIndex,
  currentOrderFirstPageIndex,
  currentOrderSize,
  totalOrdersCell,
  totalCellsInPage,
  paginationBlockSize,
  isCarousel,
  currentOrderIndex
) {
  const currentPage = Math.floor(currentOrderIndex / totalCellsInPage)
  const currentOrderFirstCellPage = Math.floor(currentOrderFirstPageIndex / totalCellsInPage)
  const firstCellOnPreviousPageIndex = Math.min(
    Math.max((currentPage - 1) * totalCellsInPage, totalCellsInPage - 1), totalOrdersCell)

  if (currentOrdersCellArrayIndex === 0) {
    if (currentOrderFirstCellPage < currentPage) {
      return firstCellOnPreviousPageIndex
    }
    return isCarousel ? totalOrdersCell - 1 : 0
  }

  if (currentOrderFirstCellPage < currentPage) {
    return firstCellOnPreviousPageIndex
  }

  return currentOrderFirstPageIndex - 1
}

function* executeCommand(commandProcessor, commandOrderId) {
  const kdsModel = yield select(getKdsModel)
  const viewsOrderArray = yield select(getViewsOrders)
  const currentOrdersCellArrayIndex = yield select(getCurrentOrder)

  const selectedView = kdsModel.views == null ? null : kdsModel.views.filter(x => x.selected)[0]
  let ordersCellArray = []
  if (selectedView != null && viewsOrderArray[selectedView.productionView] != null) {
    ordersCellArray = viewsOrderArray[selectedView.productionView]
  }

  if (selectedView == null || ordersCellArray == null) {
    return
  }

  const currentOrderCell = ordersCellArray[currentOrdersCellArrayIndex]

  let orderId = null
  if (parseInt(commandOrderId || '0', 10) !== 0) {
    orderId = commandOrderId
  } else if (currentOrderCell != null) {
    orderId = currentOrderCell.attrs.order_id
  }

  if (orderId != null) {
    commandProcessor.handleCommand(orderId, selectedView.productionView)
  }
}

function* processKdsCommand(msgBus, action) {
  const kdsModel = yield select(getKdsModel)
  const viewsOrderArray = yield select(getViewsOrders)
  const currentOrdersCellArrayIndex = yield select(getCurrentOrder)
  const paginationBlockSize = yield select(getPaginationBlockSize)
  const consolidatedItems = yield select(getConsolidatedItems)
  const selectedView = kdsModel.views == null ? null : kdsModel.views.filter(x => x.selected)[0]

  let ordersCellArray = []
  let ordersLineArray = []
  if (selectedView != null && viewsOrderArray[selectedView.productionView] != null) {
    ordersCellArray = viewsOrderArray[selectedView.productionView].orders
    ordersLineArray = viewsOrderArray[selectedView.productionView].lines
  }

  if (selectedView == null || ordersCellArray == null) {
    return
  }

  const totalCellsInPage = kdsModel.layout.rows * kdsModel.layout.cols
  const totalOrdersCell = ordersCellArray.length
  const currentOrderCell = ordersCellArray[currentOrdersCellArrayIndex]
  const currentOrderId = getOrderId(currentOrderCell)
  const currentOrderFirstPageIndex = getOrderArrayIndex(ordersCellArray, currentOrderId, 1)
  const currentOrderSize = currentOrderCell == null ? 0 : currentOrderCell.pages

  switch (action.type) {
    case eventsType.PROD_VIEW_UPDATE: {
      const productionView = action.payload.key
      const currentOrders = viewsOrderArray[productionView] != null ? viewsOrderArray[productionView].orders : []
      const ordersUpdateProcessor = new OrdersUpdateProcessor(currentOrders, kdsModel)

      if (ordersUpdateProcessor.process(action.payload.value, kdsModel.layout.lines)) {
        const newOrders = ordersUpdateProcessor.newProdOrders
        yield put({ type: eventsType.SET_VIEWS_ORDERS, payload: { key: productionView, value: newOrders } })

        if (productionView === selectedView.productionView) {
          yield changeCurrentOrderCellSelected(currentOrdersCellArrayIndex, newOrders)
        }
      }
      break
    }

    case eventsType.KDS_VIEWS_MODEL: {
      const views = action.payload || {}
      const currentView = views.filter(x => x.selected)[0]
      if (currentView == null) {
        console.error('Current view is null')
        break
      }

      const productionView = currentView.productionView
      const currentOrders = viewsOrderArray[productionView] != null ? viewsOrderArray[productionView].orders : []
      const ordersUpdateProcessor = new OrdersUpdateProcessor(currentOrders, kdsModel)

      if (ordersUpdateProcessor.process(null, kdsModel.layout.lines)) {
        const newOrders = ordersUpdateProcessor.newProdOrders
        yield put({ type: eventsType.SET_VIEWS_ORDERS, payload: { key: productionView, value: newOrders } })
      }

      break
    }

    case eventsType.KDS_LAYOUT: {
      yield changeCurrentOrderCellSelected(0, ordersCellArray)
      break
    }

    case eventsType.KDS_COMMAND: {
      let currentLine = yield select(getCurrentLine)
      const lines = ordersLineArray.length
      const line = (currentLine >= 0 && currentLine < lines) ? ordersLineArray[currentLine] : null
      if (currentLine > 0 && currentLine >= lines) {
        currentLine = lines - 1
        yield put({ type: SET_CURRENT_LINE, payload: lines - 1 })
      }

      const payload = action.payload || {}
      const attrs = payload['@attributes'] || {}
      const cmd = _.toLower(attrs.name || '')
      switch (cmd) {
        case 'bump': {
          break
        }
        case 'navigatenext': {
          const nextOrderIndex = getNextOrderIndex(
            currentOrdersCellArrayIndex,
            currentOrderFirstPageIndex,
            currentOrderSize,
            totalOrdersCell,
            totalCellsInPage,
            paginationBlockSize,
            kdsModel.carousel,
            currentOrdersCellArrayIndex)
          yield changeCurrentOrderCellSelected(nextOrderIndex, ordersCellArray)

          break
        }
        case 'navigateprevious': {
          const previousOrderIndex = getPreviousOrderIndex(
            currentOrdersCellArrayIndex,
            currentOrderFirstPageIndex,
            currentOrderSize, totalOrdersCell,
            totalCellsInPage,
            paginationBlockSize,
            kdsModel.carousel,
            currentOrdersCellArrayIndex)
          yield changeCurrentOrderCellSelected(previousOrderIndex, ordersCellArray)

          break
        }
        case 'navigateup': {
          if (currentLine > 0) {
            yield put({ type: SET_CURRENT_LINE, payload: (currentLine - 1) })
          } else {
            yield put({ type: SET_CURRENT_LINE, payload: (lines) ? lines - 1 : -1 })
          }

          break
        }
        case 'navigatedown': {
          if ((currentLine + 1) < lines) {
            yield put({ type: SET_CURRENT_LINE, payload: (currentLine + 1) })
          } else {
            yield put({ type: SET_CURRENT_LINE, payload: (lines) ? 0 : -1 })
          }

          break
        }
        case 'navigatefirst': {
          yield changeCurrentOrderCellSelected(0, ordersCellArray)
          yield put({ type: SET_CURRENT_LINE, payload: 0 })
          break
        }
        case 'recall': {
          msgBus.sendKDSUndoServe(selectedView.productionView)
          break
        }
        case 'refreshscreen': {
          yield put({ type: KDS_REFRESH_START })
          window.location.reload(true)
          break
        }
        case 'consolidateditems': {
          yield put({
            type: touchTypes.SET_CONSOLIDATED_ITEMS,
            payload: !consolidatedItems
          })
          break
        }
        case 'zoomnext': {
          yield put({ type: SET_KDS_ZOOM, payload: selectedView.productionView })
          break
        }

        case 'order_delivered':
        case 'delivered': {
          const processor = new OrderDeliveredCommandProcessor(msgBus)
          yield executeCommand(processor, attrs.orderId || currentOrderId)
          break
        }

        case 'order_served':
        case 'served': {
          const processor = new OrderServedCommandProcessor(msgBus)
          const orderId = attrs.orderId != null ? attrs.orderId : currentOrderId
          yield executeCommand(processor, orderId)
          break
        }

        case 'order_invalided':
        case 'invalidate': {
          const processor = new OrderInvalidCommandProcessor(msgBus)
          yield executeCommand(processor, attrs.orderId)
          break
        }

        case 'order_ready':
        case 'ready': {
          const processor = new OrderReadyCommandProcessor(msgBus)
          yield executeCommand(processor, attrs.orderId)
          break
        }

        case 'items_doing':
        case 'doing': {
          if (line != null) {
            const timeDelta = yield select(getTimeDelta)
            new ItemsDoingCommandProcessor(msgBus).handleCommand(line, timeDelta, selectedView.productionView)
          }
          break
        }

        case 'items_done':
        case 'done': {
          if (line != null) {
            const timeDelta = yield select(getTimeDelta)
            new ItemsDoneCommandProcessor(msgBus).handleCommand(line, timeDelta, selectedView.productionView)
          }
          break
        }

        case 'items_served':
        case 'itemsserved': {
          const processor = new ItemsServedCommandProcessor(msgBus)
          yield executeCommand(processor, currentOrderId)
          break
        }

        case 'items_delivered': {
          if (line != null) {
            const timeDelta = yield select(getTimeDelta)
            new ItemsDoneCommandProcessor(msgBus).handleCommand(line, timeDelta, selectedView.productionView, 'done')
            new ItemsDoneCommandProcessor(msgBus).handleCommand(line, timeDelta, selectedView.productionView, 'delivered')
          }

          break
        }

        case 'nextview': {
          const selectedViewIndex = kdsModel.views == null ? null : kdsModel.views.findIndex(x => x.selected)
          let viewIndex = 0
          if (selectedViewIndex !== kdsModel.views.length - 1) {
            viewIndex = selectedViewIndex + 1
          }
          yield put({ type: eventsType.SET_KDS_VIEW, payload: kdsModel.views[viewIndex].name })
          break
        }

        default: {
          break
        }
      }
      break
    }

    case eventsType.TOUCH_COMMAND: {
      const touchAction = action.payload
      const cmd = touchAction.name
      switch (cmd) {
        case touchTypes.TOUCH_SET_CURRENT_ORDER: {
          const index = touchAction.payload
          yield changeCurrentOrderCellSelected(index, ordersCellArray)

          break
        }
        case touchTypes.TOUCH_SERVE_ORDER: {
          const order = touchAction.payload
          if (order) {
            if (kdsModel.settings.onSellClick === 'delivered') {
              new OrderDeliveredCommandProcessor(msgBus).handleCommand(order, selectedView.productionView)
            } else {
              new ItemsServedCommandProcessor(msgBus).handleCommand(order, selectedView.productionView)
            }

            if (currentOrderFirstPageIndex + currentOrderSize === totalOrdersCell) {
              const previousOrderIndex = getPreviousOrderIndex(currentOrdersCellArrayIndex, currentOrderFirstPageIndex,
                currentOrderSize, totalOrdersCell, totalCellsInPage, paginationBlockSize)
              yield changeCurrentOrderCellSelected(previousOrderIndex, ordersCellArray)
            }
          }

          break
        }
        case touchTypes.TOUCH_NEXT_PAGE: {
          if (totalOrdersCell > totalCellsInPage) {
            const pageCount = Math.ceil(totalOrdersCell / totalCellsInPage)
            const currentPage = Math.floor(currentOrdersCellArrayIndex / totalCellsInPage)
            const nextPage = currentPage + 1

            const firstCellOnNextPageIndex = totalCellsInPage * nextPage
            if (nextPage >= pageCount) {
              yield changeCurrentOrderCellSelected(kdsModel.carousel ? 0 : currentOrdersCellArrayIndex, ordersCellArray)
            } else {
              yield changeCurrentOrderCellSelected(firstCellOnNextPageIndex, ordersCellArray)
            }
          }

          break
        }
        case touchTypes.TOUCH_PREVIOUS_PAGE: {
          if (totalOrdersCell > totalCellsInPage) {
            const currentPage = Math.floor(currentOrdersCellArrayIndex / totalCellsInPage)
            const previousPage = currentPage - 1

            const lastCellOnPreviousPageIndex = (totalCellsInPage * currentPage) - 1
            if (previousPage < 0) {
              yield changeCurrentOrderCellSelected(kdsModel.carousel ? ordersCellArray.length - 1 : 0, ordersCellArray)
            } else {
              yield changeCurrentOrderCellSelected(lastCellOnPreviousPageIndex, ordersCellArray)
            }
          }

          break
        }
        case touchTypes.TOUCH_DOING_LINE: {
          const timeDelta = yield select(getTimeDelta)
          new ItemsDoingCommandProcessor(msgBus).handleCommand(touchAction.payload, timeDelta, selectedView.productionView)

          break
        }
        case touchTypes.TOUCH_DONE_LINE: {
          const line = touchAction.payload
          const timeDelta = yield select(getTimeDelta)
          new ItemsDoneCommandProcessor(msgBus).handleCommand(line, timeDelta, selectedView.productionView)

          break
        }
        case touchTypes.TOUCH_SELECT_LINE: {
          const lineNumber = touchAction.payload
          yield put({ type: SET_CURRENT_LINE, payload: lineNumber })

          break
        }
        default:
          break
      }
    }
      break

    default: {
      break
    }
  }

  const updatedCurrentOrdersCellArrayIndex = yield select(getCurrentOrder)
  const updatedPaginationBlockSize = calculatedPaginationBlockSize(totalCellsInPage, updatedCurrentOrdersCellArrayIndex)
  yield changePaginationBlockSize(updatedPaginationBlockSize)
}

function* kdsSaga(kdsId) {
  const msgBus = new MessageBus(kdsId)
  yield takeEvery(
    [
      eventsType.KDS_COMMAND,
      eventsType.KDS_LAYOUT,
      eventsType.PROD_VIEW_UPDATE,
      eventsType.TOUCH_COMMAND,
      eventsType.KDS_VIEWS_MODEL
    ],
    processKdsCommand,
    msgBus
  )
}

export default kdsSaga
