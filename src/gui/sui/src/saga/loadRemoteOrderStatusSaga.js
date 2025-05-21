import { call, put, takeLatest, select } from 'redux-saga/effects'

import { MessageBus } from '3s-posui/core'
import { delay } from '3s-posui/utils'
import { RESYNC } from '3s-posui/constants/actionTypes'

import { FETCH_REMOTE_ORDER_STATUS, REMOTE_ORDER_STATUS_CHANGED } from '../constants/actionTypes'
import { getJoinedAvailableSaleTypes, getShortedSaleTypes } from '../app/util/saleTypeConverter'

const staticConfig = state => state.staticConfig
let fetchTimeout = 10000


function* fetchRemoteOrderStatus(posId) {
  try {
    const myStaticConfig = yield select(staticConfig)

    let isOnline = false
    let isOpened = false
    let lastExternalContact = null
    let closedSince = null
    let working = false

    if (myStaticConfig && myStaticConfig.remoteOrderStatus.fetchTimeout) {
      fetchTimeout = myStaticConfig.remoteOrderStatus.fetchTimeout * 1000
    }

    const msgBus = new MessageBus(posId)
    const msgBusSyncAction = msgBus.syncAction.bind(msgBus)

    if (myStaticConfig) {
      const joinedSaleTypes = getJoinedAvailableSaleTypes(myStaticConfig.availableSaleTypes)
      const saleTypes = getShortedSaleTypes(joinedSaleTypes)
      if (saleTypes.includes('DL')) {
        const response = yield call(msgBusSyncAction, 'get_remote_order_status')

        if (response != null && response.data != null && response.data !== 'False') {
          isOnline = response.data.isOnline
          isOpened = response.data.isOpened
          lastExternalContact = response.data.lastExternalContact
          closedSince = response.data.closedSince
          working = true
        }
      }
    }

    yield put({ type: REMOTE_ORDER_STATUS_CHANGED,
      payload:
        {
          'isOnline': isOnline,
          'isOpened': isOpened,
          'lastExternalContact': lastExternalContact,
          'closedSince': closedSince,
          'working': working
        }
    })
  } catch (e) {
    console.error(`Error getting remote order status: ${e}`)
  }
}

export function* loadRemoteOrderStatusSaga(posId) {
  yield takeLatest([FETCH_REMOTE_ORDER_STATUS, RESYNC], fetchRemoteOrderStatus, posId)
}

export function* reloadRemoteOrderStatusSaga() {
  let condition = true
  while (condition) {
    try {
      yield put({ type: FETCH_REMOTE_ORDER_STATUS, payload: null })
      yield call(delay, fetchTimeout)
    } catch (error) {
      condition = false
      console.error('Error fetching remote order status')
    }
  }
}
