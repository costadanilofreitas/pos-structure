import { put, call, takeLatest } from 'redux-saga/effects'
import { MessageBus } from 'posui/core'
import { delay } from 'posui/utils'
import _ from 'lodash'
import { FETCH_PRODUCT_DATA, PRODUCT_DATA_LOADED } from '../constants/actionTypes'

function* fetchProductData(posId) {
  const msgBus = new MessageBus(posId)
  const msgBusSyncAction = msgBus.syncAction.bind(msgBus)

  let payload = {}
  while (_.isEmpty(payload)) {
    try {
      const response = yield call(msgBusSyncAction, 'getProducts')
      if (!response.ok) {
        console.error('Error loading product data')
      }
      if (_.isEmpty(response.data)) yield call(delay, 1000)

      payload = response.data || {}
    } catch (e) {
      console.error('Error loading product data')
      yield call(delay, 1000)
    }
  }
  yield put({ type: PRODUCT_DATA_LOADED, payload })
}

function* loadProductDataSaga(posId) {
  yield takeLatest(FETCH_PRODUCT_DATA, fetchProductData, posId)
}

export default loadProductDataSaga

