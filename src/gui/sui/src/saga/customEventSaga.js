import { put, takeEvery } from 'redux-saga/effects'

import { CUSTOM_EVENT } from '3s-posui/constants/actionTypes'
import {
  FETCH_PRODUCT_DATA,
  MOBILE_CONFIRM_TRANSACTION,
  MOBILE_PRINT,
  SCANNER_DATA,
  STORE_MODIFIED,
  TABLE_MODIFIED
} from '../constants/actionTypes'


function* fetchCustomEvent(posId, action) {
  if (action.payload) {
    if (action.payload.TABLE_MODIFIED != null) {
      yield put({ type: TABLE_MODIFIED, payload: action.payload.TABLE_MODIFIED })
    }
    if (action.payload[`TABLE_MODIFIED-POS${posId}`] != null) {
      yield put({ type: TABLE_MODIFIED, payload: action.payload[`TABLE_MODIFIED-POS${posId}`] })
    }
    if (action.payload.STORE_MODIFIED != null) {
      yield put({ type: STORE_MODIFIED, payload: action.payload.STORE_MODIFIED })
    }
    if (action.payload[`STORE_MODIFIED-POS${posId}`] != null) {
      yield put({ type: STORE_MODIFIED, payload: action.payload[`STORE_MODIFIED-POS${posId}`] })
    }
    if (action.payload.MOBILE_PRINT != null) {
      yield put({ type: MOBILE_PRINT, payload: action.payload.MOBILE_PRINT })
    }
    if (action.payload.MOBILE_CONFIRM_TRANSACTION != null) {
      yield put({ type: MOBILE_CONFIRM_TRANSACTION, payload: action.payload.MOBILE_CONFIRM_TRANSACTION })
    }
    if (action.payload.SCANNER_DATA != null) {
      yield put({ type: SCANNER_DATA, payload: action.payload.SCANNER_DATA })
    }
    if (action.payload.RUPTURE_MODIFIED != null) {
      yield put({ type: FETCH_PRODUCT_DATA, payload: '0' })
    }
  }
}

function* customEventSaga(posId) {
  yield takeEvery([CUSTOM_EVENT], fetchCustomEvent, posId.toString().padStart(2, '0'))
}

export default customEventSaga

