import { put, call, takeLatest, race } from 'redux-saga/effects'
import _ from 'lodash'

import { MessageBus } from '3s-posui/core'
import { delay } from '3s-posui/utils'
import { RESYNC } from '3s-posui/constants/actionTypes'

import { FETCH_PRODUCT_DATA, PRODUCT_DATA_LOADED } from '../constants/actionTypes'


function* fetchProductData(posId, action) {
  const msgBus = new MessageBus(posId)
  const msgBusSyncAction = msgBus.syncAction.bind(msgBus)
  const secondsToRenewCache = action.payload != null ? action.payload : ''

  let payload = null
  while (payload == null) {
    try {
      const { response, timeout } = yield race({
        response: call(msgBusSyncAction, 'getProducts', secondsToRenewCache),
        timeout: delay(5000)
      })

      if (timeout || response == null || !response.ok || !_.isObject(response.data)) {
        console.error(`Error loading Products data. Response: ${response} / Timeout: ${timeout}`)
      } else {
        payload = response.data
        yield put({ type: PRODUCT_DATA_LOADED, payload: payload || null })
      }
    } catch (e) {
      console.error('Error loading product data')
    }

    yield call(delay, 1000)
  }
}

function* loadProductDataSaga(posId) {
  yield takeLatest([FETCH_PRODUCT_DATA, RESYNC], fetchProductData, posId)
}

export default loadProductDataSaga

