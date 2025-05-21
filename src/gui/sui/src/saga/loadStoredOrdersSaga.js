import { call, put, takeLatest, select } from 'redux-saga/effects'

import { MessageBus } from '3s-posui/core'
import { delay } from '3s-posui/utils'
import { RESYNC } from '3s-posui/constants/actionTypes'

import { FETCH_STORED_ORDERS, STORED_ORDERS_CHANGED } from '../constants/actionTypes'

const staticConfig = state => state.staticConfig
let fetchTimeout = 5000


function* fetchStoredOrders(posId) {
  try {
    const myStaticConfig = yield select(staticConfig)
    if (myStaticConfig && myStaticConfig.fetchStoredOrdersTimeout) {
      fetchTimeout = (myStaticConfig.fetchStoredOrdersTimeout * 1000)
    }

    const msgBus = new MessageBus(posId)
    const msgBusSyncAction = msgBus.syncAction.bind(msgBus)

    const response = yield call(msgBusSyncAction, 'get_stored_orders', true, true, true)
    yield put({ type: STORED_ORDERS_CHANGED, payload: response.data })
  } catch (e) {
    console.error('Error fetching stored orders')
  }
}

export function* loadStoredOrdersSaga(posId) {
  yield takeLatest([FETCH_STORED_ORDERS, RESYNC], fetchStoredOrders, posId)
}

export function* reloadStoredOrdersSaga() {
  let condition = true
  while (condition) {
    try {
      yield put({ type: FETCH_STORED_ORDERS, payload: null })
      yield call(delay, fetchTimeout)
    } catch (error) {
      condition = false
      console.error('Error fetching stored orders')
    }
  }
}
